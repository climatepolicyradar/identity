// Values from Pulumi outputs — set these as environment variables in your app.
// Vite: import.meta.env.VITE_*
// Next.js: process.env.NEXT_PUBLIC_*

export const COGNITO_DOMAIN = import.meta.env.VITE_COGNITO_DOMAIN;
// e.g. "identity-production.auth.us-east-1.amazoncognito.com"

export const CLIENT_ID = import.meta.env.VITE_COGNITO_CLIENT_ID;
// Pulumi output: app_client_id

export const REDIRECT_URI = import.meta.env.VITE_REDIRECT_URI ?? "http://localhost:3000/callback";

export const COGNITO_LOGOUT_URI = `https://${COGNITO_DOMAIN}/logout`;
export const COGNITO_AUTHORIZE_URI = `https://${COGNITO_DOMAIN}/oauth2/authorize`;
export const COGNITO_TOKEN_URI = `https://${COGNITO_DOMAIN}/oauth2/token`;
