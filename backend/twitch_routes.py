from flask import Blueprint, redirect, request, session, jsonify
import requests, urllib.parse
from backend.config import TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, TWITCH_REDIRECT_URI
from backend.db import save_user_token

twitch_bp = Blueprint('twitch', __name__)

AUTH_URL = "https://id.twitch.tv/oauth2/authorize"
TOKEN_URL = "https://id.twitch.tv/oauth2/token"
SCOPES = [
    'chat:read',
    'chat:edit',
    'channel:manage:broadcast'
]

@twitch_bp.route("/login")
def twitch_login():
    params={
        'client_id': TWITCH_CLIENT_ID,
        'redirect_uri': TWITCH_REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(SCOPES),
        'force_verify': 'true'
    }
    return redirect(f"{AUTH_URL}?{urllib.parse.urlencode(params)}")

@twitch_bp.route("/callback")
def twitch_callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Missing Code"}), 400
    token_params = {
        'client_id': TWITCH_CLIENT_ID,
        'client_secret': TWITCH_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': TWITCH_REDIRECT_URI
    }
    token_res = request.post(TOKEN_URL, params=token_params)
    token_info = token_res.json()

    headers = {
        "Authorization": f"Bearer {token_info['access_token']}",
        "Client_Id": TWITCH_CLIENT_ID
    }
    #user_res = requests.get("https://api.twitch.tv/helix/users", headers=headers)
    #user_data = user_res.json()
    #user_id = user_data["data"][0]["id"]
    user_res = requests.get("https://api.twitch.tv/helix/users", headers=headers)
    user_data = user_res.json()["data"][0]
    user_id = user_data["id"]

    # Store tokens in our DB
    save_user_token(user_id, "twitch", {
        "access_token": token_info["access_token"],
        "refresh_token": token_info.get("refresh_token"),
        "expires_in": token_info["expires_in"],
        "scope": token_info["scope"],
        "channel": user_data["data"][0]["login"]
    })

    return redirect("/success")

@twitch_bp.route("/test")
def test_route():
    return "Twitch route works!"