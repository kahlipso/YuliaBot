import requests, re, json

async def queue_song_for_user(query, token):
    headers = {'Authorization': f'Bearer {token}'}

    #First check for direct link to song request
    match = re.search(r'(spotify:track:[\w\d]+|open\.spotify\.com/track/([\w\d]+))', query)
    if match:
        track_id = match.group(2) if match.group(2) else match.group(1).split(':')[-1]
    else:
        # Search Spotify
        r = requests.get(
            'https://api.spotify.com/v1/search',
            headers=headers,
            params={'q': query, 'type': 'track', 'limit': 1}
        )
        res = r.json()
        try:
            track_id = res['tracks']['items'][0]['id']
        except (KeyError, IndexError, json.JSONDecodeError):
            return "Couldn't find that song."

    # Queue the song
    uri = f'spotify:track:{track_id}'
    r2 = requests.post(
        'https://api.spotify.com/v1/me/player/queue',
        headers=headers,
        params={'uri': uri}
    )

    if r2.status_code in range(200, 300):
        track = requests.get(f"https://api.spotify.com/v1/tracks/{track_id}", headers=headers).json()
        title = track.get("name")
        artist = track["artists"][0]["name"]
        return f"Queued: {title} by {artist}"
    else:
        return "Failed to queue this song."