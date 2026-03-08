import json
import pulumi
import pulumi_aws as aws

config = pulumi.Config()

# --- Required config ---------------------------------------------------------
google_client_id = config.require("google_client_id")
google_client_secret = config.require_secret("google_client_secret")
cognito_domain_prefix = config.require("cognito_domain_prefix")

# --- Optional config with sensible defaults ----------------------------------
allowed_email_domain = config.get("allowed_email_domain") or "climatepolicyradar.org"
callback_urls: list[str] = config.get_object("callback_urls") or [
    "http://localhost:3000/callback"
]
logout_urls: list[str] = config.get_object("logout_urls") or [
    "http://localhost:3000"
]

stack = pulumi.get_stack()
project = pulumi.get_project()
region = aws.get_region().name

tags = {
    "Project": project,
    "Stack": stack,
    "ManagedBy": "pulumi",
}

# --- Pre-signup Lambda (domain restriction) ----------------------------------
lambda_role = aws.iam.Role(
    "pre-signup-lambda-role",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }],
    }),
    tags=tags,
)

aws.iam.RolePolicyAttachment(
    "pre-signup-lambda-logs",
    role=lambda_role.name,
    policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
)

pre_signup_lambda = aws.lambda_.Function(
    "pre-signup",
    name=f"{project}-{stack}-pre-signup",
    runtime="python3.12",
    handler="index.handler",
    role=lambda_role.arn,
    environment=aws.lambda_.FunctionEnvironmentArgs(
        variables={"ALLOWED_DOMAIN": allowed_email_domain},
    ),
    code=pulumi.AssetArchive({
        "index.py": pulumi.StringAsset("""\
import os

ALLOWED_DOMAIN = os.environ["ALLOWED_DOMAIN"]

def handler(event, context):
    email = event["request"]["userAttributes"].get("email", "")
    if not email.endswith(f"@{ALLOWED_DOMAIN}"):
        raise Exception(f"Access restricted to @{ALLOWED_DOMAIN} accounts.")
    # Auto-confirm federated users so they don't get stuck in a pending state
    event["response"]["autoConfirmUser"] = True
    event["response"]["autoVerifyEmail"] = True
    return event
"""),
    }),
    tags=tags,
)

# Allow Cognito to invoke the Lambda
aws.lambda_.Permission(
    "pre-signup-lambda-permission",
    action="lambda:InvokeFunction",
    function=pre_signup_lambda.name,
    principal="cognito-idp.amazonaws.com",
)

# --- Cognito User Pool -------------------------------------------------------
user_pool = aws.cognito.UserPool(
    "user-pool",
    name=f"{project}-{stack}",
    username_attributes=["email"],
    auto_verified_attributes=["email"],
    password_policy=aws.cognito.UserPoolPasswordPolicyArgs(
        minimum_length=8,
        require_lowercase=True,
        require_uppercase=True,
        require_numbers=True,
        require_symbols=False,
    ),
    account_recovery_setting=aws.cognito.UserPoolAccountRecoverySettingArgs(
        recovery_mechanisms=[
            aws.cognito.UserPoolAccountRecoverySettingRecoveryMechanismArgs(
                name="verified_email",
                priority=1,
            ),
        ],
    ),
    lambda_config=aws.cognito.UserPoolLambdaConfigArgs(
        pre_sign_up=pre_signup_lambda.arn,
    ),
    tags=tags,
)

# Allow Cognito to invoke the Lambda (source ARN scoped to this user pool)
aws.lambda_.Permission(
    "pre-signup-lambda-permission-scoped",
    action="lambda:InvokeFunction",
    function=pre_signup_lambda.name,
    principal="cognito-idp.amazonaws.com",
    source_arn=user_pool.arn,
)

# --- Google OIDC Identity Provider -------------------------------------------
google_idp = aws.cognito.IdentityProvider(
    "google-idp",
    user_pool_id=user_pool.id,
    provider_name="Google",
    provider_type="Google",
    provider_details={
        "client_id": google_client_id,
        "client_secret": google_client_secret,
        "authorize_scopes": "openid email profile",
    },
    attribute_mapping={
        "email": "email",
        "name": "name",
        "username": "sub",
        "picture": "picture",
    },
)

# --- Cognito Hosted UI Domain -------------------------------------------------
user_pool_domain = aws.cognito.UserPoolDomain(
    "user-pool-domain",
    domain=cognito_domain_prefix,
    user_pool_id=user_pool.id,
)

# --- App Client --------------------------------------------------------------
app_client = aws.cognito.UserPoolClient(
    "app-client",
    name=f"{project}-{stack}-client",
    user_pool_id=user_pool.id,
    generate_secret=False,
    allowed_oauth_flows=["code"],
    allowed_oauth_flows_user_pool_client=True,
    allowed_oauth_scopes=["openid", "email", "profile"],
    callback_urls=callback_urls,
    logout_urls=logout_urls,
    supported_identity_providers=["Google"],
    explicit_auth_flows=[
        "ALLOW_REFRESH_TOKEN_AUTH",
        "ALLOW_USER_SRP_AUTH",
    ],
    opts=pulumi.ResourceOptions(depends_on=[google_idp]),
)

# --- Outputs -----------------------------------------------------------------
pulumi.export("user_pool_id", user_pool.id)
pulumi.export("user_pool_arn", user_pool.arn)
pulumi.export("app_client_id", app_client.id)
pulumi.export(
    "cognito_issuer",
    pulumi.Output.concat(
        "https://cognito-idp.", region, ".amazonaws.com/", user_pool.id
    ),
)
pulumi.export(
    "hosted_ui_base_url",
    f"https://{cognito_domain_prefix}.auth.{region}.amazoncognito.com",
)
pulumi.export(
    "authorization_endpoint",
    f"https://{cognito_domain_prefix}.auth.{region}.amazoncognito.com/oauth2/authorize",
)
pulumi.export(
    "token_endpoint",
    f"https://{cognito_domain_prefix}.auth.{region}.amazoncognito.com/oauth2/token",
)
