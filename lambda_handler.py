from spotify_auth import create_spotify_app
from magnum import Magnum

app=create_spotify_app()
handler=Magnum(app)