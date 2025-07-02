from flask import Flask, redirect, request, session, jsonify
from flask_cors import CORS
import urllib.parse
import requests
from datetime import datetime
import os, json





def create_spotify_app():
    app = Flask(__name__)
    CORS(app)
    app.secret_key = 'yulia-secrect-key123123'#os.getenv('APP_SECRET_KEY')

    CLIENT_ID = 'aab78aa660354b16afc3bdacd93755ce'#os.getenv('SPOTIFY_CLIENT_ID') 
    CLIENT_SECRET = '43d5d05bfbe44b898e02d34b81b87b20'#os.getenv('SPOTIFY_CLIENT_SECRET')
    REDIRECT_URI = 'http://127.0.0.1:5000/callback'#os.getenv('SPOTIFY_REDIRECT_URI')

    AUTH_URL = 'https://accounts.spotify.com/authorize'
    TOKEN_URL = 'https://accounts.spotify.com/api/token'
    API_BASE_URL = 'https://api.spotify.com/v1/'
    
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
            'show_dialog': True
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

            with open('spotify_token.json', 'w') as f:
                json.dump({'access_token': token_info['access_token']}, f)

            return redirect('/playlists')
        
    @app.route('/playlists')
    def get_playlists():
        if 'access_token' not in session:
            return redirect('/login')
        
        if datetime.now().timestamp() > session['expires_at']:
            return redirect('/refresh-token')
        
        headers = {
            'Authorization': f"Bearer {session['access_token']}"
        }

        response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)
        playlists = response.json()

        return jsonify(playlists)

    @app.route('/refresh-token')
    def refresh_token():
        if 'refresh_token' not in session:
            return redirect('/login')
        
        if datetime.now().timestamp() > session['expires_at']:
            req_body = {
                'grant_type': 'refresh_token',
                'refresh_token': session['refresh_token'],
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET
            }

            response = requests.post(TOKEN_URL, data=req_body)
            new_token_info = response.json()

            session['access_token'] = new_token_info['access_token']
            session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

            return redirect('/playlists')
    
    @app.route('/spotify-token')
    def get_token():
        if 'access_token' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        return jsonify({'token': session['access_token']})

    return app

    
        