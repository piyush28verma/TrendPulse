"""
LinkedIn OAuth 2.0 Token Generator
Run this script once to get your LinkedIn access token.
Usage: python3 get_linkedin_token.py
Reads LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET from .env
"""
import http.server
import urllib.parse
import webbrowser
import requests
import sys
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")
REDIRECT_URI = "http://localhost:9876/callback"
SCOPES = "openid profile w_member_social"

if not CLIENT_ID or not CLIENT_SECRET:
    print("ERROR: Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET in .env first")
    sys.exit(1)

auth_code = None

class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Success!</h1><p>Close this tab.</p></body></html>")
        elif "error" in params:
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            error = params.get("error_description", params.get("error", ["Unknown"]))[0]
            self.wfile.write(f"<html><body><h1>Error</h1><p>{error}</p></body></html>".encode())
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, format, *args):
        pass

def main():
    global auth_code
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&scope={urllib.parse.quote(SCOPES)}"
    )
    print("\n=== LinkedIn OAuth Token Generator ===\n")
    print(f"Visit: {auth_url}\n")
    webbrowser.open(auth_url)
    server = http.server.HTTPServer(("localhost", 9876), CallbackHandler)
    print("Waiting for callback...")
    while auth_code is None:
        server.handle_request()
    server.server_close()
    print(f"\nGot code. Exchanging for token...")
    token_resp = requests.post("https://www.linkedin.com/oauth/v2/accessToken", data={
        "grant_type": "authorization_code", "code": auth_code,
        "redirect_uri": REDIRECT_URI, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
    })
    if token_resp.status_code != 200:
        print(f"ERROR: {token_resp.status_code} - {token_resp.text}")
        sys.exit(1)
    token_data = token_resp.json()
    access_token = token_data.get("access_token", "")
    print(f"Token obtained! Expires in {token_data.get('expires_in', 0) // 86400} days.")
    profile_resp = requests.get("https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"})
    person_urn = ""
    if profile_resp.status_code == 200:
        profile = profile_resp.json()
        person_urn = f"urn:li:person:{profile.get('sub', '')}"
        print(f"Profile: {profile.get('name', '?')} ({person_urn})")
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    with open(env_path, "r") as f:
        content = f.read()
    if "LINKEDIN_ACCESS_TOKEN" in content:
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            if line.startswith("LINKEDIN_ACCESS_TOKEN="):
                new_lines.append(f"LINKEDIN_ACCESS_TOKEN={access_token}")
            elif line.startswith("LINKEDIN_PERSON_URN=") and person_urn:
                new_lines.append(f"LINKEDIN_PERSON_URN={person_urn}")
            else:
                new_lines.append(line)
        content = "\n".join(new_lines)
    else:
        content += f"\nLINKEDIN_ACCESS_TOKEN={access_token}\nLINKEDIN_PERSON_URN={person_urn}\n"
    with open(env_path, "w") as f:
        f.write(content)
    print(f"Updated .env! Restart backend to use new credentials.")

if __name__ == "__main__":
    main()
