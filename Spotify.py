"""
deezer_to_spotify.py
────────────────────
Transfers a public Deezer playlist to a new Spotify playlist.

Author: Daniel Joy
Version: 2.0.0

Setup:
  1. Create a Spotify app at https://developer.spotify.com/dashboard
  2. Copy your Client ID and Client Secret into a .env file:
       SPOTIFY_CLIENT_ID=your_id
       SPOTIFY_CLIENT_SECRET=your_secret
  3. In your Spotify app settings, add this Redirect URI:
       http://127.0.0.1:8000/callback
  4. Install dependencies:
       pip install spotipy requests python-dotenv

Usage:
  Set DEEZER_DEEPLINK below to your Deezer playlist share link, then run:
       python deezer_to_spotify.py
"""

import os
import re
import time
import requests
import spotipy
from pathlib import Path
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────
#  CONFIGURATION  –  edit these values before running
# ─────────────────────────────────────────────────────────────

DEEZER_DEEPLINK   = ""          # Paste your Deezer share link here
SPOTIFY_PLAYLIST_NAME = "Deezer Import"   # Name for the new Spotify playlist
SPOTIFY_PLAYLIST_PUBLIC = False           # True = public, False = private
REDIRECT_URI = "http://127.0.0.1:8000/callback"

# ─────────────────────────────────────────────────────────────
#  DEEZER
# ─────────────────────────────────────────────────────────────

def resolve_deezer_playlist_id(deeplink: str) -> str:
    """
    Follows redirects on a Deezer share link and extracts the numeric playlist ID.

    Args:
        deeplink: A Deezer share URL (e.g. https://deezer.page.link/...)

    Returns:
        The playlist ID as a string.

    Raises:
        ValueError: If no playlist ID can be found in the resolved URL.
    """
    session = requests.Session()
    response = session.head(deeplink, allow_redirects=True)
    final_url = response.url

    match = re.search(r'playlist/(\d+)', final_url)
    if not match:
        raise ValueError(f"Could not extract playlist ID from URL: {final_url}")

    return match.group(1)


def fetch_deezer_tracks(playlist_id: str) -> list[dict]:
    """
    Fetches all tracks from a public Deezer playlist, handling pagination.

    The Deezer API returns 25 tracks per page by default; this function
    iterates through every page until all tracks are collected.

    Args:
        playlist_id: The numeric Deezer playlist ID.

    Returns:
        A list of dicts with keys 'artist' and 'title'.

    Raises:
        Exception: If the Deezer API returns a non-200 status code.
    """
    tracks = []
    url = f"https://api.deezer.com/playlist/{playlist_id}/tracks"
    params = {"limit": 100, "index": 0}

    while url:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Deezer API error {response.status_code}: {response.text}")

        data = response.json()

        for track in data.get("data", []):
            tracks.append({
                "artist": track["artist"]["name"],
                "title":  track["title"],
            })

        # Deezer pagination: follow the 'next' URL if present
        url = data.get("next")
        params = {}  # 'next' already contains query params

    return tracks

# ─────────────────────────────────────────────────────────────
#  SPOTIFY
# ─────────────────────────────────────────────────────────────

def build_spotify_client() -> spotipy.Spotify:
    """
    Creates an authenticated Spotipy client using OAuth.

    Credentials are read from environment variables (via .env):
        SPOTIFY_CLIENT_ID
        SPOTIFY_CLIENT_SECRET

    The OAuth token cache is stored in ~/.spotify-cache/token.cache
    so re-authentication is not needed on subsequent runs.

    Returns:
        An authenticated spotipy.Spotify instance.
    """
    cache_dir = Path.home() / ".spotify-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=REDIRECT_URI,
        scope="playlist-modify-public playlist-modify-private",
        cache_path=str(cache_dir / "token.cache"),
    ))


def create_spotify_playlist(sp: spotipy.Spotify, name: str, public: bool = False) -> str:
    """
    Creates a new empty Spotify playlist for the current user.

    Args:
        sp:     Authenticated Spotipy client.
        name:   Display name for the new playlist.
        public: Whether the playlist should be public (default: False).

    Returns:
        The Spotify playlist ID of the newly created playlist.
    """
    user_id = sp.current_user()["id"]
    playlist = sp.user_playlist_create(
        user=user_id,
        name=name,
        public=public,
        description="Imported from Deezer via deezer_to_spotify.py",
    )
    return playlist["id"]


def search_tracks_on_spotify(sp: spotipy.Spotify, tracks: list[dict]) -> tuple[list[str], list[str]]:
    """
    Searches Spotify for each track and collects their URIs.

    Uses a precise 'track:<title> artist:<artist>' query first.
    Falls back to a looser title-only query if the precise one returns nothing,
    which helps with tracks where artist names differ slightly between platforms.

    To stay within Spotify's rate limits, a small delay is added every 10 requests.

    Args:
        sp:     Authenticated Spotipy client.
        tracks: List of dicts with 'artist' and 'title' keys.

    Returns:
        A tuple of:
          - found_uris:  List of Spotify track URIs that were matched.
          - not_found:   List of 'Artist – Title' strings that had no match.
    """
    found_uris = []
    not_found  = []

    total = len(tracks)
    for i, track in enumerate(tracks, start=1):
        artist = track["artist"]
        title  = track["title"]

        print(f"  [{i}/{total}] Searching: {artist} – {title}", end="\r")

        try:
            # Precise query
            query = f"track:{title} artist:{artist}"
            results = sp.search(q=query, type="track", limit=1)
            items = results["tracks"]["items"]

            # Fallback: title only
            if not items:
                results = sp.search(q=f"track:{title}", type="track", limit=1)
                items = results["tracks"]["items"]

            if items:
                found_uris.append(items[0]["uri"])
            else:
                not_found.append(f"{artist} – {title}")

        except Exception as e:
            print(f"\n  ⚠️  Error searching '{title}': {e}")
            not_found.append(f"{artist} – {title}")

        # Gentle rate-limit guard: pause every 10 requests
        if i % 10 == 0:
            time.sleep(0.3)

    print()  # newline after the \r progress line
    return found_uris, not_found


def add_tracks_to_playlist(sp: spotipy.Spotify, playlist_id: str, track_uris: list[str]) -> None:
    """
    Adds track URIs to a Spotify playlist in batches of 100 (API limit).

    Args:
        sp:          Authenticated Spotipy client.
        playlist_id: The target Spotify playlist ID.
        track_uris:  List of Spotify track URIs to add.
    """
    for i in range(0, len(track_uris), 100):
        batch = track_uris[i:i + 100]
        sp.playlist_add_items(playlist_id, batch)
        print(f"  ✅ Added tracks {i + 1}–{i + len(batch)}")

# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("🎵  DEEZER → SPOTIFY PLAYLIST TRANSFER")
    print("=" * 60)

    if not DEEZER_DEEPLINK:
        print("❌ DEEZER_DEEPLINK is empty. Set it at the top of this file.")
        return

    # ── Step 1: Resolve Deezer playlist ───────────────────────
    print("\n📡 Resolving Deezer link...")
    try:
        playlist_id = resolve_deezer_playlist_id(DEEZER_DEEPLINK)
        print(f"   Playlist ID: {playlist_id}")
    except ValueError as e:
        print(f"❌ {e}")
        return

    print("📋 Fetching tracks from Deezer...")
    try:
        deezer_tracks = fetch_deezer_tracks(playlist_id)
    except Exception as e:
        print(f"❌ {e}")
        return
    print(f"   {len(deezer_tracks)} track(s) found on Deezer")

    # ── Step 2: Authenticate with Spotify ─────────────────────
    print("\n🔐 Connecting to Spotify...")
    try:
        sp = build_spotify_client()
        user = sp.current_user()
        print(f"   Logged in as: {user['display_name']} ({user['id']})")
    except Exception as e:
        print(f"❌ Spotify authentication failed: {e}")
        return

    # ── Step 3: Create destination playlist ───────────────────
    print(f"\n📁 Creating Spotify playlist: '{SPOTIFY_PLAYLIST_NAME}'...")
    try:
        spotify_playlist_id = create_spotify_playlist(sp, SPOTIFY_PLAYLIST_NAME, SPOTIFY_PLAYLIST_PUBLIC)
        print(f"   Playlist created (ID: {spotify_playlist_id})")
    except Exception as e:
        print(f"❌ Could not create playlist: {e}")
        return

    # ── Step 4: Search and match tracks ───────────────────────
    print(f"\n🔍 Searching {len(deezer_tracks)} tracks on Spotify...")
    found_uris, not_found = search_tracks_on_spotify(sp, deezer_tracks)
    print(f"   ✅ Matched: {len(found_uris)}  |  ❌ Not found: {len(not_found)}")

    # ── Step 5: Add matched tracks ────────────────────────────
    if found_uris:
        print(f"\n➕ Adding {len(found_uris)} tracks to the playlist...")
        try:
            add_tracks_to_playlist(sp, spotify_playlist_id, found_uris)
        except Exception as e:
            print(f"❌ Error adding tracks: {e}")
            return

    # ── Summary ───────────────────────────────────────────────
    playlist_url = f"https://open.spotify.com/playlist/{spotify_playlist_id}"
    print(f"\n{'=' * 60}")
    print(f"✅  Transfer complete!")
    print(f"   Transferred : {len(found_uris)} / {len(deezer_tracks)} tracks")
    print(f"   🔗 {playlist_url}")

    if not_found:
        print(f"\n⚠️  {len(not_found)} track(s) not found on Spotify:")
        for t in not_found:
            print(f"   - {t}")


if __name__ == "__main__":
    main()