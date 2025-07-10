from flask import Blueprint, redirect, request, session, jsonify
import requests, urllib.parse, base64
from datetime import  datetime
from backend.config import SPOTIFY_CLIENT_SECRET, SPOTIFY_CLIENT_ID, REDIRECT_URI
from backend.db import save_user_token

spotify_bp = Blueprint('spotify', __name__)

@spotify_bp.route("/login")
def login():
    scope = 'user-read-private user-read-email user-modify-playback-state'
    params = {
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True
    }
    return redirect("https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params))


@spotify_bp.route("/callback")
def callback():
    try:
        code = request.args.get("code")
        if not code:
            return jsonify({"error": "Missing code"}), 400

        # Step 1: Base64 encode client credentials
        client_creds = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
        b64_creds = base64.b64encode(client_creds.encode()).decode()

        headers = {
            "Authorization": f"Basic {b64_creds}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI
        }

        # Step 2: Exchange code for token
        token_res = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
        print("Raw token response:", token_res.text)
        token_info = token_res.json()

        access_token = token_info.get("access_token")
        if not access_token:
            return jsonify({"error": "No access token returned", "details": token_info}), 400

        # Step 3: Use access token to get user info
        user_headers = {"Authorization": f"Bearer {access_token}"}
        user_res = requests.get("https://api.spotify.com/v1/me", headers=user_headers)
        print("User info response:", user_res.text)

        user_data = user_res.json()
        user_id = user_data.get("id")
        if not user_id:
            return jsonify({"error": "Could not fetch user ID", "details": user_data}), 400

        # Step 4: Save token
        save_user_token(user_id, "spotify", {
            "access_token": access_token,
            "refresh_token": token_info.get("refresh_token"),
            "expires_in": token_info.get("expires_in")
        })

        return redirect("/success")

    except Exception as e:
        print("Error in /callback:", e)
        return jsonify({"error": str(e)}), 500
