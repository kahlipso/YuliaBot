from twitchAPI.twitch import Twitch
from twitchAPI.chat import Chat, ChatMessage, ChatCommand, EventData
from twitchAPI.type import ChatEvent, AuthScope
from twitchAPI.oauth import UserAuthenticator
import asyncio, json, re, requests
from backend.db import get_user_token, get_all_users
from backend.config import TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, TWITCH_REDIRECT_URI
from bot.utils import queue_song_for_user
from backend.token_utils import refresh_spotify_token, refresh_twitch_token

SCOPES = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT, AuthScope.CHANNEL_MANAGE_BROADCAST]

#store active chat objects
active_chats = {}

async def on_ready(event: EventData):
    print(f"Connected to Twitch chat for {event.user_name}")

async def on_message(msg: ChatMessage):
    print(f"{msg.user.display_name}: {msg.text}")

async def song_request(cmd: ChatCommand):
    user_channel = cmd.channel.name
    user_id = cmd.channel.channel_id
    song_query = cmd.parameter
    

    if not song_query:
        await cmd.reply("Use this command like: !sr <song name> or !sr <song share link>")
        return
    
    spotify_token = refresh_spotify_token(user_id)
    if not spotify_token:
        await cmd.reply("Spotify token expired or missing. Please reauthenticate.")
        return

    result = await queue_song_for_user(song_query, spotify_token["access_token"])
    await cmd.reply(result)

async def run_bot():
    twitch = await Twitch(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)

    users = get_all_users()
    
    for user_id, user_data in users.items():
        twitch_token = refresh_twitch_token(user_id)#user_data.get("twitch")
        if not twitch_token:
            print(f"User {user_id} needs to reauthenticate with Twitch")
            return

        #if not twitch_token:
            #continue

        try: 
            await twitch.set_user_authentication(
                twitch_token["access_token"],
                SCOPES,
                twitch_token["refresh_token"]
            )

            chat = await Chat(twitch, initial_channel=[user_data["twitch"]["channel"]])
            chat.register_event(ChatEvent.READY, on_ready)
            chat.register_event(ChatEvent.MESSAGE, on_message)
            chat.register_command("sr", song_request)

            chat.start()
            active_chats[user_id] = chat

        except Exception as e:
            print(f"YuliaBot failed to start for {user_id}: {e}")


