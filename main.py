from threading import Thread
from flask import Flask
import os
from spotify_auth import create_spotify_app
from twitch_bot import run_bot

# Initialize Flask app with Spotify routes
app = create_spotify_app()

def start_twitch_bot():
    import asyncio
    asyncio.run(run_bot())

if __name__ == '__main__':
    # Start Twitch bot in background thread
    Thread(target=start_twitch_bot, daemon=True).start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))