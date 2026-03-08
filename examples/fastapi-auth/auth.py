"""
Cognito JWT validation dependency for FastAPI.

Set these environment variables:
  COGNITO_USER_POOL_ID  e.g. us-east-1_abc123
  COGNITO_CLIENT_ID     Pulumi output: app_client_id
  AWS_REGION            e.g. us-east-1
"""

import os
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

USER_POOL_ID = os.environ["COGNITO_USER_POOL_ID"]
CLIENT_ID = os.environ["COGNITO_CLIENT_ID"]
REGION = os.environ.get("AWS_REGION", "us-east-1")
ISSUER = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}"
JWKS_URL = f"{ISSUER}/.well-known/jwks.json"

bearer = HTTPBearer()


@lru_cache(maxsize=1)
def _get_jwks() -> jwt.PyJWKClient:
    return jwt.PyJWKClient(JWKS_URL)


class AuthenticatedUser(BaseModel):
    sub: str
    email: str = ""
    name: str = ""

    model_config = {"extra": "allow"}  # preserve any additional Cognito claims


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> AuthenticatedUser:
    token = credentials.credentials
    try:
        signing_key = _get_jwks().get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
            issuer=ISSUER,
            options={"verify_exp": True},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return AuthenticatedUser(**claims)
