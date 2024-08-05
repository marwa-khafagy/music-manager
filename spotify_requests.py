import json
import requests
from flask import jsonify, redirect, render_template
from datetime import datetime
import global_functions
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_BASE_URL = os.getenv('API_BASE_URL')
AR_GENRES = os.getenv('ARAB_GENRES')

def get_playlists(session):
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    headers = global_functions.get_auth_header(session['access_token'])
    response = requests.get(f"{API_BASE_URL}me/playlists", headers=headers)
    
    if response.status_code != 200:
        print("Failed to fetch playlists:", response.status_code)
        return jsonify({'error': 'Failed to fetch playlists'}), 500

    playlists = response.json().get('items', [])
    return render_template('playlists.html', playlists=playlists)

def get_liked_tracks(session):
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    headers = global_functions.get_auth_header(session['access_token'])

    try:
        response = requests.get(f"{API_BASE_URL}me/tracks?limit=50", headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Failed to fetch tracks:", e)
        return jsonify({'error': 'Failed to fetch tracks'}), 500

    tracks = response.json().get('items', [])
    for idx, track in enumerate(tracks):
        print(f"{idx+1}. {track['track']['name']}")

    return tracks

def get_recent_ar_tracks(session):
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    tracks = get_liked_tracks(session)
    ar_tracks = [track for track in tracks if is_ar_track(session, track['track'])]
    return render_template('liked.html', tracks=ar_tracks)

def is_ar_track(session, track):
    artist_id = track['artists'][0]['id']
    # artist_id = get_artist_id(session, artist_name)

    if artist_id is None:
        return False

    genres = get_genre_by_artist(session, artist_id)
    for genre in genres:
        genre_words = genre.split()
        for word in genre_words:
            if word in AR_GENRES:
                return True
    
    return False

def get_artist_id(session, artist_name):
    url = f'{API_BASE_URL}search'
    headers = global_functions.get_auth_header(session['access_token'])
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query

    try:
        response = requests.get(query_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Failed to fetch artist:", e)
        return jsonify({'error': 'Failed to fetch artist'}), 500

    try:
        artists = response.json()["artists"]["items"]
    except (json.JSONDecodeError, KeyError) as e:
        print("JSON parsing error or key error:", e)
        return jsonify({'error': 'Failed to parse artist data'}), 500

    if not artists:
        print(f"Artist {artist_name} not found")
        return None

    return artists[0]["id"]

def get_genre_by_artist(session, artist_id):
    url = f"{API_BASE_URL}artists/{artist_id}"
    headers = global_functions.get_auth_header(session['access_token'])

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Failed to fetch artist genres:", e)
        return jsonify({'error': 'Failed to fetch artist genres'}), 500

    try:
        genres = response.json().get("genres", [])
    except (json.JSONDecodeError, KeyError) as e:
        print("JSON parsing error or key error:", e)
        return jsonify({'error': 'Failed to parse artist genres'}), 500

    return genres
