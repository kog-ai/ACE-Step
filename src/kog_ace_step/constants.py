import os


MUSIC_URL = os.environ.get("MUSIC_URL", "0.0.0.0")
MUSIC_PORT = int(os.environ.get("MUSIC_PORT", "8080"))
