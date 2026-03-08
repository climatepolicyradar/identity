import http.server
import urllib.parse
import webbrowser

CLIENT_ID = "2pmi4c8u3niv93bdao6g6nfmb6"
DOMAIN = "https://identity-production.auth.us-east-1.amazoncognito.com"
REDIRECT = "http://localhost:3000"

auth_url = (
    f"{DOMAIN}/oauth2/authorize"
    f"?client_id={CLIENT_ID}"
    f"&response_type=code"
    f"&scope=openid+email+profile"
    f"&redirect_uri={REDIRECT}"
)


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        code = params.get("code", [None])[0]
        error = params.get("error_description", params.get("error", [None]))[0]

        self.send_response(200)
        self.end_headers()

        if code:
            print(f"\nAuth code received: {code}")
            print("Login successful.")
            self.wfile.write(b"Login successful - you can close this tab.")
        else:
            print(f"\nLogin failed: {error}")
            self.wfile.write(f"Login failed: {error}".encode())

    def log_message(self, format, *args):
        pass  # suppress request logging noise


print(f"Opening browser to: {auth_url}")
webbrowser.open(auth_url)
http.server.HTTPServer(("", 3000), Handler).handle_request()
