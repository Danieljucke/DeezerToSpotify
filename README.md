Voici un exemple de fichier `README.md` que tu pourrais utiliser pour ton projet. Il décrit comment faire fonctionner le code étape par étape.

---

# Deezer to Spotify Playlist Transfer

Ce projet permet de transférer une playlist depuis Deezer vers Spotify. Il récupère les titres d'une playlist Deezer et les ajoute à une nouvelle playlist Spotify via l'API de chaque service.

## Prérequis

Avant d'exécuter ce script, tu dois avoir les éléments suivants :

- **Un compte Spotify Developer** : [Crée un compte Spotify Developer](https://developer.spotify.com/dashboard/applications) et génère un `client_id` et un `client_secret` pour l'authentification avec l'API Spotify.
- **Un compte Deezer** avec un lien vers une playlist publique.

## Installation

1. Clone ce repository ou télécharge les fichiers sur ton ordinateur.
   
2. Assure-toi d'avoir Python installé sur ton système (version 3.6 ou supérieure).

3. Installe les dépendances nécessaires :
   ```bash
   pip install spotipy requests
   ```

## Configuration

1. **Spotify API :**  
   - Va sur le [Dashboard de Spotify Developer](https://developer.spotify.com/dashboard/applications).
   - Crée une nouvelle application pour obtenir ton `client_id` et `client_secret`.
   - Remplis les informations dans le script Python à la section suivante :

   ```python
   sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
       client_id="VOTRE_CLIENT_ID",  # Remplace par ton client_id
       client_secret="VOTRE_CLIENT_SECRET",  # Remplace par ton client_secret
       redirect_uri="http://localhost:8888/callback",
       scope="playlist-modify-public",
       cache_path=cache_file
   ))
   ```

2. **Deezer Playlist :**
   - Récupère le lien de la playlist Deezer que tu souhaites transférer. Par exemple, un lien de playlist ressemblant à ceci : `https://www.deezer.com/fr/playlist/123456789`.
   - Mets ce lien dans le script à la ligne suivante :
   
   ```python
   DEEPLINK = "TON_LIEN_DEEPLER"
   ```

## Utilisation

1. **Exécution du script :**
   
   Une fois que tu as configuré le `client_id`, `client_secret` et le lien de ta playlist Deezer, tu peux lancer le script avec la commande suivante :

   ```bash
   python deezer_to_spotify.py
   ```

2. **Processus d'exécution :**
   
   Le script suit les étapes suivantes :
   - **Extraction de l'ID de la playlist Deezer** : Il suit les redirections du lien Deezer et extrait l'ID de la playlist.
   - **Récupération des titres de la playlist Deezer** : Il récupère les informations des titres de la playlist (nom de l'artiste et titre de la chanson) depuis l'API Deezer.
   - **Configuration de Spotify** : Le script configure l'authentification avec l'API Spotify à l'aide des informations d'authentification que tu as fournies.
   - **Création d'une playlist sur Spotify** : Il crée une nouvelle playlist sur ton compte Spotify avec le nom "Playlist Deezer" (ou un autre nom que tu peux définir).
   - **Recherche et ajout des titres à la playlist Spotify** : Le script recherche chaque titre sur Spotify et l'ajoute à la playlist. Si un titre n'est pas trouvé, il est noté dans la sortie.

3. **Exemple de sortie :**
   
   Lorsque tout se passe bien, tu devrais voir quelque chose comme ceci dans le terminal :
   ```bash
   🎵 ID récupéré : 123456789
   Récupération des titres depuis Deezer...
   Nombre de titres trouvés: 50
   Configuration de Spotify...
   Création de la playlist Spotify...
   Ajout des titres à la playlist Spotify...
   Transfert terminé avec succès!
   ```

## Remarques

- **Limite de requêtes Spotify** : Spotify impose une limite sur le nombre de requêtes par minute. Si tu as une playlist avec beaucoup de titres, tu pourrais être temporairement bloqué si tu dépasses cette limite. Le script tente de gérer cela, mais il peut être nécessaire de ralentir les appels API dans des cas extrêmes.
  
- **Titres non trouvés** : Si certains titres ne sont pas trouvés sur Spotify, ils seront affichés dans la sortie, ce qui te permettra de vérifier manuellement.

## Licence

Ce projet est sous licence MIT. N'hésite pas à l'utiliser et à l'adapter à tes besoins !

---

Ce format de `README.md` fournit toutes les informations nécessaires pour configurer et exécuter le script dans un environnement local.
