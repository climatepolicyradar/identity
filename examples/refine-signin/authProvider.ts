import type { AuthProvider } from "@refinedev/core";
import {
  CLIENT_ID,
  COGNITO_AUTHORIZE_URI,
  COGNITO_LOGOUT_URI,
  REDIRECT_URI,
} from "./config";

// Token storage keys
const ID_TOKEN_KEY = "cpr_id_token";
const ACCESS_TOKEN_KEY = "cpr_access_token";

// Decode a JWT payload without verifying the signature.
// For signature verification, use a proper JWT library server-side.
function decodeJwtPayload(token: string): Record<string, unknown> {
  const base64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
  return JSON.parse(atob(base64));
}

function isTokenExpired(token: string): boolean {
  try {
    const { exp } = decodeJwtPayload(token) as { exp?: number };
    if (!exp) return true;
    return Date.now() / 1000 > exp;
  } catch {
    return true;
  }
}

export const authProvider: AuthProvider = {
  // Redirect to Cognito hosted UI → Google SSO
  login: async () => {
    const params = new URLSearchParams({
      response_type: "code",
      client_id: CLIENT_ID,
      redirect_uri: REDIRECT_URI,
      scope: "openid email profile",
      identity_provider: "Google",
    });
    window.location.href = `${COGNITO_AUTHORIZE_URI}?${params}`;
    // Return success=false so refine doesn't try to navigate — we're already redirecting.
    return { success: false };
  },

  // Called by CallbackPage after exchanging the code for tokens
  check: async () => {
    const token = localStorage.getItem(ID_TOKEN_KEY);
    if (!token || isTokenExpired(token)) {
      localStorage.removeItem(ID_TOKEN_KEY);
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      return { authenticated: false, redirectTo: "/login" };
    }
    return { authenticated: true };
  },

  logout: async () => {
    localStorage.removeItem(ID_TOKEN_KEY);
    localStorage.removeItem(ACCESS_TOKEN_KEY);

    const params = new URLSearchParams({
      client_id: CLIENT_ID,
      logout_uri: window.location.origin,
    });
    window.location.href = `${COGNITO_LOGOUT_URI}?${params}`;
    return { success: true };
  },

  getIdentity: async () => {
    const token = localStorage.getItem(ID_TOKEN_KEY);
    if (!token) return null;
    try {
      const payload = decodeJwtPayload(token) as {
        email?: string;
        name?: string;
        picture?: string;
      };
      return {
        email: payload.email,
        name: payload.name,
        avatar: payload.picture,
      };
    } catch {
      return null;
    }
  },

  onError: async (error) => {
    if (error?.status === 401 || error?.status === 403) {
      return { logout: true, redirectTo: "/login" };
    }
    return { error };
  },
};

// Exported so CallbackPage can store tokens after the code exchange
export function storeTokens(idToken: string, accessToken: string) {
  localStorage.setItem(ID_TOKEN_KEY, idToken);
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
}
