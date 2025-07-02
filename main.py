from threading import Thread
from spotify_auth import create_spotify_app
from twitch_bot import run_bot
import asyncio, webbrowser, time
app = create_spotify_app()

def start_twitch_bot():
    asyncio.run(run_bot())

def open_link():
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    
    # Start Twitch bot in background thread
    Thread(target=start_twitch_bot, daemon=True).start()

    Thread(target=open_link, daemon=True).start()
    
    # Run Flask app
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
    #app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))