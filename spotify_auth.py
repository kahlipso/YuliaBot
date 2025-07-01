from flask import Flask, redirect, request, session, jsonify
import urllib.parse
import requests
from datetime import datetime
import os


CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID') 
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'


def create_spotify_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('APP_SECRET_KEY')

    
    @app.route('/')
    def home():
        return "This is YuliaBot <a href='/login'>Login with Spotify</a>"

    @app.route('/login')
    def login():
        scope = 'user-read-private user-read-email user-modify-playback-state'

        params = {
            'client_id': CLIENT_ID,
            'response_type': 'code',
            'scope': scope,
            'redirect_uri': REDIRECT_URI,
        }

        auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

        return redirect(auth_url)

    @app.route('/callback')
    def callback():
        if 'error' in request.args:
            return jsonify({"error": request.args['error']})
        
        if 'code' in request.args:
            req_body = {
                'code': request.args['code'],
                'grant_type': 'authorization_code',
                'redirect_uri': REDIRECT_URI,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET
            }
            response = requests.post(TOKEN_URL, data=req_body)
            token_info = response.json()

            session['access_token'] = token_info['access_token']
            session['refresh_token'] = token_info['refresh_token']
            session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
            return redirect('/')
        
    @app.route('/spotify-token')
    def get_token():
        if 'access_token' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        return jsonify({'token': session['access_token']})

    return app