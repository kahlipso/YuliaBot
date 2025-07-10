from flask import Flask
from flask_cors import CORS
from backend.spotify_routes import spotify_bp
from backend.twitch_routes import twitch_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "yulia_secret_keyy393884712"
    CORS(app)

    app.register_blueprint(spotify_bp, url_prefix = "/spotify")
    app.register_blueprint(twitch_bp, url_prefix = "/twitch")

    return app
