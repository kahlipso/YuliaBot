from datetime import datetime, timedelta
import requests
from backend.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET
from backend.db import get_user_token, save_user_token

def is_expired(last_updated, expires_in, buffer_seconds=60):
    updated = datetime.fromisoformat(last_updated)
    return datetime.utcnow() > updated + timedelta(seconds=expires_in - buffer_seconds)

def refresh_spotify_token(user_id):
    token_data = get_user_token(user_id, "spotify")
    if not token_data:
        return None

    if not is_expired(token_data["last_updated"], token_data["expires_in"]):
        return token_data["access_token"]

    # Refresh token
    headers = {
        "Authorization": f"Basic {requests.auth._basic_auth_str(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": token_data["refresh_token"]
    }

    res = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    print("Spotify refresh response:", res.text)
    if res.status_code != 200:
        return None

    new_data = res.json()
    token_data["access_token"] = new_data["access_token"]
    token_data["expires_in"] = new_data.get("expires_in", token_data["expires_in"])

    save_user_token(user_id, "spotify", token_data)
    return token_data["access_token"]

def refresh_twitch_token(user_id):
    token_data = get_user_token(user_id, "twitch")
    if not token_data:
        return None

    if not is_expired(token_data["last_updated"], token_data["expires_in"]):
        return token_data["access_token"]

    data = {
        "grant_type": "refresh_token",
        "refresh_token": token_data["refresh_token"],
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET
    }

    res = requests.post("https://id.twitch.tv/oauth2/token", data=data)
    print("Twitch refresh response:", res.text)
    if res.status_code != 200:
        return None

    new_data = res.json()
    token_data["access_token"] = new_data["access_token"]
    token_data["expires_in"] = new_data.get("expires_in", token_data["expires_in"])

    save_user_token(user_id, "twitch", token_data)
    return token_data["access_token"]
