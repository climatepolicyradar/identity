import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { CLIENT_ID, COGNITO_TOKEN_URI, REDIRECT_URI } from "./config";
import { storeTokens } from "./authProvider";

// Mount this at /callback in your router.
// Cognito redirects here with ?code=… after successful Google sign-in.
export function CallbackPage() {
  const navigate = useNavigate();
  const exchanged = useRef(false); // prevent double-fire in React StrictMode

  useEffect(() => {
    if (exchanged.current) return;
    exchanged.current = true;

    const code = new URLSearchParams(window.location.search).get("code");
    if (!code) {
      navigate("/login", { replace: true });
      return;
    }

    exchangeCode(code)
      .then(() => navigate("/", { replace: true }))
      .catch(() => navigate("/login", { replace: true }));
  }, [navigate]);

  return <p style={{ textAlign: "center", marginTop: "4rem" }}>Signing in…</p>;
}

async function exchangeCode(code: string) {
  const body = new URLSearchParams({
    grant_type: "authorization_code",
    client_id: CLIENT_ID,
    redirect_uri: REDIRECT_URI,
    code,
  });

  const res = await fetch(COGNITO_TOKEN_URI, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });

  if (!res.ok) throw new Error(`Token exchange failed: ${res.status}`);

  const { id_token, access_token } = await res.json();
  storeTokens(id_token, access_token);
}
