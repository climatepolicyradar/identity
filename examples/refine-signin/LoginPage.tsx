import { useLogin } from "@refinedev/core";

// Minimal sign-in page. Drop your own styling/layout around this.
export function LoginPage() {
  const { mutate: login, isLoading } = useLogin();

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Climate Policy Radar</h1>
        <p style={styles.subtitle}>Sign in with your CPR Google account</p>
        <button
          onClick={() => login({})}
          disabled={isLoading}
          style={styles.button}
        >
          {isLoading ? "Redirecting…" : "Sign in with Google"}
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "100vh",
    background: "#f5f5f5",
  },
  card: {
    background: "#fff",
    borderRadius: 8,
    padding: "2.5rem",
    boxShadow: "0 2px 12px rgba(0,0,0,0.1)",
    textAlign: "center" as const,
    maxWidth: 360,
    width: "100%",
  },
  title: { margin: "0 0 0.5rem", fontSize: "1.5rem" },
  subtitle: { color: "#666", margin: "0 0 1.5rem", fontSize: "0.9rem" },
  button: {
    width: "100%",
    padding: "0.75rem",
    fontSize: "1rem",
    cursor: "pointer",
    borderRadius: 4,
    border: "1px solid #ccc",
    background: "#fff",
  },
} as const;
