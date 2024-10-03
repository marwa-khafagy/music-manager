import json
import requests
from flask import jsonify, redirect, render_template
# for refresh token 
from datetime import datetime

# for environment variables
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GENRES = os.getenv('GENRES')
PLAYLIST_ID = os.getenv('PLAYLIST_ID')

API_BASE_URL = "https://api.spotify.com/v1/"


def get_auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def get_liked_tracks(session, offset):
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    headers = get_auth_header(session['access_token'])

    try:
        response = requests.get(f"{API_BASE_URL}me/tracks?limit=50&offset={offset}", headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Failed to fetch tracks:", e)
        return jsonify({'error': 'Failed to fetch tracks'}), 500

    tracks = response.json().get('items', [])

    return tracks

# prints all liked tracks of chosen genre(s) in terminal
# prints all ar songs not in the playlist in web 
# input 'recent_tracks' to get run this
def add_recent_tracks(session):
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    # fetches last 100 liked tracks
    liked_tracks = get_liked_tracks(session, 0) + get_liked_tracks(session, 50)
    
    # filters liked tracks to genre tracks 
    ar_tracks = [track for track in liked_tracks if is_ar_track(session, track['track'])]

    # fetches all tracks in the ar playlist
    playlist = get_ar_playlist(session)

    # gets all track ids in the playlist
    playlist_track_ids = {track['track']['id'] for track in playlist if track['track']}

    # filters out and prints tracks that are in the playlist
    unique_ar_tracks = []
    idx = 1
    track_ids = []
    print("Liked tracks of your chosen genre already in the playlist:")
    for track in ar_tracks:
        if track['track']['id'] not in playlist_track_ids:
            unique_ar_tracks.append(track)
            track_ids.append(f"spotify:track:{track['track']['id']}")
        else:
            print(f"{idx + 1}.{track['track']['name']}")
            idx += 1
    print(track_ids)
    if len(track_ids) == 0:
        print("No new tracks to add")
        return render_template('liked.html', tracks=unique_ar_tracks)
    
    return add_songs_to_playlist(session, track_ids, unique_ar_tracks)
    # return render_template('liked.html', tracks=unique_ar_tracks)

# checks if the track is part of genre
def is_ar_track(session, track):
    artist_id = track['artists'][0]['id']
    if artist_id is None:
        return False

    # list of genres associated with the artist
    genres = get_genre_by_artist(session, artist_id)

    # checks if any of the genres are in our genre(s)
    for genre in genres:
        genre_words = genre.split()
        for word in genre_words:
            if word in GENRES:
                return True
    
    return False

# returns an artist's id given their name
# not used in the final code
def get_artist_id(session, artist_name):
    url = f'{API_BASE_URL}search'
    headers = get_auth_header(session['access_token'])
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query

    # try to get artist
    try:
        response = requests.get(query_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Failed to fetch artist:", e)
        return jsonify({'error': 'Failed to fetch artist'}), 500

    # parses the possible artists
    try:
        artists = response.json()["artists"]["items"]
    except (json.JSONDecodeError, KeyError) as e:
        print("JSON parsing error or key error:", e)
        return jsonify({'error': 'Failed to parse artist data'}), 500

    if not artists:
        print(f"Artist {artist_name} not found")
        return None
    
    # returns the first artist's id
    return artists[0]["id"]

# checks the genres that the artist is associated with
def get_genre_by_artist(session, artist_id):
    url = f"{API_BASE_URL}artists/{artist_id}"
    headers = get_auth_header(session['access_token'])

    # try to get artist genres
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Failed to fetch artist genres:", e)
        return jsonify({'error': 'Failed to fetch artist genres'}), 500

    # parses the genres
    try:
        genres = response.json().get("genres", [])
    except (json.JSONDecodeError, KeyError) as e:
        print("JSON parsing error or key error:", e)
        return jsonify({'error': 'Failed to parse artist genres'}), 500

    return genres

# returns all the track id's in the playlist
def get_ar_playlist(session):
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    headers = get_auth_header(session['access_token'])

    # fetches the number of songs in the playlist
    num_of_songs = requests.get(f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?fields=total", headers=headers)
    num_of_songs = num_of_songs.json()['total']
    
    offset = 0
    songs = []

    # fetches all the songs in the playlist, by 100 songs at a time
    while offset < num_of_songs:
        response = requests.get(f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?fields=items.track.id&limit=100&offset={offset}", headers=headers)
        if response.status_code != 200:
            print("Failed to fetch playlists:", response.status_code)
            return jsonify({'error': 'Failed to fetch playlists'}), 500
        playlist = response.json()
        songs.extend(playlist['items'])
        offset += 100
    
    return songs


def add_songs_to_playlist(session, track_ids, unique_ar_tracks):
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    headers = get_auth_header(session['access_token'])

    # adds the unique tracks to the playlist
    req_body = {
        'uris': track_ids
    }
    response = requests.post(f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks", headers=headers, json=req_body)
    if response.status_code != 201:
            print("Failed to fetch playlists:", response.json())
            return jsonify({'error': 'Failed to fetch playlists'}), 500

    return render_template('liked.html', tracks=unique_ar_tracks)


