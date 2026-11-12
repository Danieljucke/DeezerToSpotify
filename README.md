# Deezer to Spotify Playlist Transfer

A Python tool for transferring public Deezer playlists to Spotify. It retrieves songs from Deezer, searches for matching tracks on Spotify, and adds them to a newly created Spotify playlist.

## Features

- **Playlist transfer:** Import tracks from a public Deezer playlist into a new Spotify playlist.
- **Paginated retrieval:** Fetch songs across multiple Deezer API pages, including larger playlists.
- **Track matching:** Search Spotify by title and artist, with a title-only fallback.
- **OAuth authentication:** Connect securely using your Spotify developer application.
- **Customizable destination:** Choose the Spotify playlist name and public/private visibility.
- **Transfer summary:** Display matched tracks, unmatched tracks, and the new playlist URL.
- **Basic rate-limit precaution:** Pause briefly after every 10 Spotify searches.

## Requirements

Before getting started, make sure you have:

- Python **3.9 or newer**.
- A Spotify account and a [Spotify Developer application](https://developer.spotify.com/dashboard).
- A public Deezer playlist URL.
- An internet connection.

A Deezer account is not required to retrieve publicly accessible playlists.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Danieljucke/DeezerToSpotify.git
cd DeezerToSpotify
```

### 2. Install dependencies

```bash
python -m pip install spotipy requests python-dotenv
```

On Windows, you can use `py` instead of `python`.

## Configuration

### 1. Configure Spotify API credentials

1. Open the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. Create an application.
3. Copy your Client ID and Client Secret.
4. Add the following redirect URI to your Spotify application's settings:

```text
http://127.0.0.1:8000/callback
```

The redirect URI must match the `REDIRECT_URI` value in `Spotify.py`.

### 2. Set up environment variables

Copy `.env.example` to `.env`.

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

**Linux/macOS:**

```bash
cp .env.example .env
```

Edit `.env` and enter your Spotify credentials:

```dotenv
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

**Security:** Never commit your `.env` file or expose your Spotify Client Secret.

### 3. Configure your playlist

Open `Spotify.py` and modify these variables:

```python
DEEZER_DEEPLINK = "https://www.deezer.com/en/playlist/123456789"

SPOTIFY_PLAYLIST_NAME = "Deezer Import"

SPOTIFY_PLAYLIST_PUBLIC = False
```

| Variable | Description |
|---|---|
| `DEEZER_DEEPLINK` | Public Deezer playlist or share URL |
| `SPOTIFY_PLAYLIST_NAME` | Name of the new Spotify playlist |
| `SPOTIFY_PLAYLIST_PUBLIC` | `True` for public, `False` for private |

The default playlist visibility is private.

## Usage

Run the script from the repository directory:

```bash
python Spotify.py
```

Or on Windows:

```powershell
py Spotify.py
```

On the first run, Spotify may ask you to authorize the application.

The script requests `playlist-modify-public` and `playlist-modify-private` permissions.

### How it works

1. **Resolve Deezer playlist:** Follow Deezer URL redirects and extract the playlist ID.
2. **Retrieve tracks:** Fetch available track information using the Deezer API.
3. **Authenticate with Spotify:** Establish an authorized Spotify API connection.
4. **Create a Spotify playlist:** Create a new playlist using your configured name and visibility.
5. **Match tracks:** Search using the song title and artist, with a title-only fallback.
6. **Add songs:** Add matched tracks in batches of up to 100.
7. **Display results:** Show the completed transfer count, unmatched tracks, and new playlist URL.

### Example output

The following is an abbreviated example:

```text
🎵  DEEZER → SPOTIFY PLAYLIST TRANSFER

📡 Resolving Deezer link...
   Playlist ID: 123456789

📋 Fetching tracks from Deezer...
   50 track(s) found on Deezer

🔐 Connecting to Spotify...
   Logged in as: Example User (example_user)

📁 Creating Spotify playlist: 'Deezer Import'...

🔍 Searching 50 tracks on Spotify...
   ✅ Matched: 47  |  ❌ Not found: 3

➕ Adding 47 tracks to the playlist...
   ✅ Added tracks 1–47

✅  Transfer complete!
   Transferred : 47 / 50 tracks
   🔗 https://open.spotify.com/playlist/...

⚠️  3 track(s) not found on Spotify:
   - Example Artist – Example Song
```

Actual results depend on playlist contents and track availability.

## Troubleshooting

| Problem | Possible solution |
|---|---|
| `DEEZER_DEEPLINK is empty` | Configure the playlist URL inside `Spotify.py`. |
| Invalid Deezer playlist ID | Check that your URL resolves to a valid public playlist. |
| Spotify authentication failure | Check your credentials, application access, and redirect URI. |
| Missing tracks | Check whether the songs exist on Spotify under different titles or artists. |
| Spotify rate limiting | Retry later or reduce request frequency. |

## Limitations

- **One-way transfers:** Only Deezer-to-Spotify transfers are supported.
- **Public Deezer playlists:** Private Deezer playlists requiring authentication are not supported.
- **Matching accuracy:** Similar titles and alternate releases may result in incorrect matches.
- **Unmatched tracks:** Songs unavailable on Spotify cannot be transferred automatically.
- **New playlist per execution:** Each run creates a new Spotify playlist rather than synchronizing an existing one.
- **Rate limits:** The built-in delay is a basic precaution, not comprehensive retry or exponential-backoff handling.

## Privacy and security

Spotify credentials are loaded from environment variables rather than embedded in the source code.

The script also maintains a local OAuth token cache at:

```text
~/.spotify-cache/token.cache
```

Keep this file private because it may contain active authentication tokens.

The application communicates with Spotify and Deezer through their APIs. No separate application backend is required by the current script.

## Project structure

```text
DeezerToSpotify/
├── .env.example
├── .gitignore
├── README.md
└── Spotify.py
```

## Contributing

Contributions, suggestions, and bug reports are welcome.

You can open an issue through the [GitHub Issues page](https://github.com/Danieljucke/DeezerToSpotify/issues).

When submitting changes, please describe what was changed and how it was tested.

## Disclaimer

This is an independent open-source project and is not affiliated with, endorsed by, or sponsored by Spotify or Deezer.

Spotify and Deezer are trademarks of their respective owners.

## License status

No root license file is currently provided. Until the repository owner selects
and adds a license, copyright law reserves reuse rights by default. The
documentation does not make a license choice on the owner's behalf.
