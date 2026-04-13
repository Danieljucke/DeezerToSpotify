# Deezer to Spotify Playlist Transfer

This project allows you to transfer a playlist from Deezer to Spotify. It retrieves tracks from a Deezer playlist and adds them to a new Spotify playlist using each service's API.

## Prerequisites

Before running this script, you need the following:

- **A Spotify Developer account**: [Create a Spotify Developer account](https://developer.spotify.com/dashboard/applications) and generate a `client_id` and `client_secret` for Spotify API authentication.
- **A Deezer account** with a link to a public playlist.

## Installation

1. Clone this repository or download the files to your computer.
   
2. Make sure you have Python installed on your system (version 3.6 or higher).

3. Install the required dependencies:
   ```bash
   pip install spotipy requests
   ```

## Configuration

1. **Spotify API:**  
   - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications).
   - Create a new application to get your `client_id` and `client_secret`.
   - Fill in the information in the Python script in the following section:

   ```python
   sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
       client_id="YOUR_CLIENT_ID",  # Replace with your client_id
       client_secret="YOUR_CLIENT_SECRET",  # Replace with your client_secret
       redirect_uri="http://localhost:8888/callback",
       scope="playlist-modify-public",
       cache_path=cache_file
   ))
   ```

2. **Deezer Playlist:**
   - Get the link of the Deezer playlist you want to transfer. For example, a playlist link looks like this: `https://www.deezer.com/en/playlist/123456789`.
   - Put this link in the script at the following line:
   
   ```python
   DEEPLINK = "YOUR_DEEZER_LINK"
   ```

## Usage

1. **Running the script:**
   
   Once you have configured the `client_id`, `client_secret`, and your Deezer playlist link, you can run the script with the following command:

   ```bash
   python deezer_to_spotify.py
   ```

2. **Execution process:**
   
   The script follows these steps:
   - **Extract Deezer playlist ID**: It follows the Deezer link redirects and extracts the playlist ID.
   - **Retrieve Deezer playlist tracks**: It fetches track information (artist name and song title) from the Deezer API.
   - **Configure Spotify**: The script sets up authentication with the Spotify API using the credentials you provided.
   - **Create a Spotify playlist**: It creates a new playlist on your Spotify account named "Deezer Playlist" (or another name you can customize).
   - **Search and add tracks to Spotify playlist**: The script searches for each track on Spotify and adds it to the playlist. If a track isn't found, it's noted in the output.

3. **Example output:**
   
   When everything works correctly, you should see something like this in the terminal:
   ```bash
   🎵 Retrieved ID: 123456789
   Retrieving tracks from Deezer...
   Number of tracks found: 50
   Configuring Spotify...
   Creating Spotify playlist...
   Adding tracks to Spotify playlist...
   Transfer completed successfully!
   ```

## Notes

- **Spotify rate limits**: Spotify imposes limits on the number of requests per minute. If you have a playlist with many tracks, you might be temporarily blocked if you exceed this limit. The script attempts to handle this, but you may need to slow down API calls in extreme cases.
  
- **Tracks not found**: If some tracks are not found on Spotify, they will be displayed in the output, allowing you to check them manually.