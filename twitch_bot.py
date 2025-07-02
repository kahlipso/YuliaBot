from twitchAPI.chat import Chat, EventData, ChatMessage, ChatCommand
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
import os
import asyncio
import requests
import json
import re

APP_ID = 'ls72qs51sxj0p6x2flr86v3808glbf'#os.getenv('TWITCH_APP_ID')
APP_SECRET = 'dqcryq0eb8tgo9to0qykepuh1kcag9'#os.getenv('TWITCH_APP_SECRET')
USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT, AuthScope.CHANNEL_MANAGE_BROADCAST]
target_channels = 'kahlipso_'#os.getenv('TWITCH_CHANNELS')

bot_started = False

async def on_message(msg: ChatMessage):
    print(f'{msg.user.display_name} - {msg.text}')

async def on_ready(ready_event: EventData):
    await ready_event.chat.join_room(target_channels)

def get_spotify_token():
    with open('spotify_token.json') as f:
        return json.load(f)['access_token']

async def song_request(cmd: ChatCommand):
    query = cmd.parameter
    if not query:
        await cmd.reply("Use this command by entering: !sr <song name>")
        return
    
    #try:
        #token_response = requests.get('http://127.0.0.1:5000/spotify-token')
        #token_data = token_response.json()
        #if not token_data.get('token'):
        #    await cmd.reply("Spotify not connected. Please visit /login")
        #    return
        #token = token_data['token']
    #except:
        #await cmd.reply("Error connecting to Spotify")
        #return
    token = get_spotify_token()
    headers = {'Authorization': f'Bearer {token}'}
    match = re.search(r'(spotify:track:[\w\d]+|open\.spotify\.com/track/([\w\d]+))', query)

    if match:
        # Extract track ID from URL or URI and build the full URI
        track_id = match.group(2) if match.group(2) else match.group(1).split(':')[-1]
        uri = f'spotify:track:{track_id}'

        # Optional: get track metadata to show feedback
        r = requests.get(f'https://api.spotify.com/v1/tracks/{track_id}', headers=headers)
        if r.status_code != 200:
            return "Failed to find the track info."
        track_data = r.json()
        title = track_data['name']
        artist = track_data['artists'][0]['name']

        if 200 <= r2.status_code < 300:
            return f"Queued: {title} by {artist}"
        else:
            return "Failed to queue this song."

    else:

        search_params = {'q': query, 'type': 'track', 'limit': 1}
        r = requests.get('https://api.spotify.com/v1/search', headers=headers, params=search_params)
        res = r.json()

        try:
            uri = res['tracks']['items'][0]['uri']
            title=res['tracks']['items'][0]['name']
            artist = res['tracks']['items'][0]['artists'][0]['name']
        except (KeyError, IndexError):
            return "Couldn't find that song."
        
        r2 = requests.post('https://api.spotify.com/v1/me/player/queue', headers=headers, params={'uri': uri})

        if 200 <= r2.status_code < 300:
            return f"Queued: {title} by {artist}"
        else:
            return "Failed to queue this song."



async def run_bot():
    global bot_started
    if bot_started:
        return
    bot_started = True

    bot = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(bot, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await bot.set_user_authentication(token, USER_SCOPE, refresh_token)

    chat = await Chat(bot)

    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)

    chat.register_command('sr', song_request)
    chat.start()
    
    