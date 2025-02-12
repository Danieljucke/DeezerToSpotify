import os
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pathlib import Path


# Go to that link to get your client_id and secrent_client_id on spotify https://developer.spotify.com/dashboard


def get_deezer_playlist_id(deeplink):
    session = requests.Session()
    response = session.head(deeplink, allow_redirects=True)
    final_url = response.url  # URL complète après redirection
    # Extraire uniquement l'ID de la playlist (nombre avant le premier "?")
    match = re.search(r'playlist/(\d+)', final_url)
    playlist_id = match.group(1) if match else None
    return playlist_id

def get_deezer_playlist_tracks(playlist_id):
    """Récupère les titres d'une playlist Deezer"""
    url = f"https://api.deezer.com/playlist/{playlist_id}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Erreur lors de la récupération de la playlist Deezer")
    
    playlist_data = response.json()
    tracks = []
    
    for track in playlist_data['tracks']['data']:
        artist = track['artist']['name']
        title = track['title']
        tracks.append({
            'artist': artist,
            'title': title
        })
    
    return tracks

def setup_spotify():
    """Configure l'authentification Spotify"""
    # Crée un dossier .spotify-cache dans le répertoire utilisateur
    cache_path = os.path.join(str(Path.home()), '.spotify-cache')
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)
    
    cache_file = os.path.join(cache_path, 'token.cache')
    
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id="VOTRE_CLIENT_ID", #Put Your client id here
        client_secret="VOTRE_CLIENT_SECRET",
        redirect_uri="http://localhost:8888/callback",
        scope="playlist-modify-public",
        cache_path=cache_file
    ))

def create_spotify_playlist(sp, playlist_name):
    """Crée une nouvelle playlist Spotify"""
    try:
        user_id = sp.current_user()['id']
        playlist = sp.user_playlist_create(user_id, playlist_name)
        return playlist['id']
    except Exception as e:
        print(f"Erreur lors de la création de la playlist: {str(e)}")
        raise

def search_and_add_tracks(sp, tracks, playlist_id):
    """Recherche et ajoute les titres à la playlist Spotify"""
    track_uris = []
    not_found = []
    
    for track in tracks:
        try:
            query = f"track:{track['title']} artist:{track['artist']}"
            results = sp.search(q=query, type='track', limit=1)
            
            if results['tracks']['items']:
                track_uri = results['tracks']['items'][0]['uri']
                track_uris.append(track_uri)
            else:
                not_found.append(f"{track['artist']} - {track['title']}")
        except Exception as e:
            print(f"Erreur lors de la recherche de {track['title']}: {str(e)}")
    
    # Ajoute les titres par lots de 100
    for i in range(0, len(track_uris), 100):
        batch = track_uris[i:i + 100]
        try:
            sp.playlist_add_items(playlist_id, batch)
        except Exception as e:
            print(f"Erreur lors de l'ajout du lot {i//100 + 1}: {str(e)}")
    
    if not_found:
        print("\nTitres non trouvés sur Spotify:")
        for track in not_found:
            print(f"- {track}")

def main():
    #Put your Deezer playlist link here
    DEEPLINK=""
    # ID de la playlist Deezer
    DEEZER_PLAYLIST_ID =get_deezer_playlist_id(DEEPLINK)
    print(f"🎵 ID récupéré : {DEEZER_PLAYLIST_ID}")
    
    try:
        # Récupère les titres de la playlist Deezer
        print("Récupération des titres depuis Deezer...")
        deezer_tracks = get_deezer_playlist_tracks(DEEZER_PLAYLIST_ID)
        print(f"Nombre de titres trouvés: {len(deezer_tracks)}")
        
        # Configure Spotify
        print("Configuration de Spotify...")
        sp = setup_spotify()
        
        # Crée une nouvelle playlist Spotify
        print("Création de la playlist Spotify...")
        spotify_playlist_id = create_spotify_playlist(sp, "Playlist Deezer") #you can change the name of your playlist here
        
        # Ajoute les titres à la playlist Spotify
        print("Ajout des titres à la playlist Spotify...")
        search_and_add_tracks(sp, deezer_tracks, spotify_playlist_id)
        
        print("\nTransfert terminé avec succès!")
        
    except Exception as e:
        print(f"\nUne erreur est survenue: {str(e)}")

if __name__ == "__main__":
    main()