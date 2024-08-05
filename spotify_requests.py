import json
import requests 
from flask import jsonify, redirect, render_template
from datetime import datetime
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
API_BASE_URL = os.getenv('API_BASE_URL')
AR_GENRES = os.getenv('ARAB_GENRES')

def get_playlists(session):
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    response = requests.get(f"{API_BASE_URL}me/playlists", headers=headers)
    playlists = response.json().get('items', [])
    
    # Render the template with the playlists data
    return render_template('playlists.html', playlists=playlists)

def get_liked_tracks(session):
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    try:
        response = requests.get(f"{API_BASE_URL}me/tracks?limit=50", headers=headers)
        response.raise_for_status()  # Raise an error for bad HTTP status codes
    except requests.exceptions.RequestException as e:
        print("Failed to fetch tracks:", e)
        return jsonify({'error': 'Failed to fetch tracks'}), 500

    # data = response.json()
    # tracks = data.get('items', [])
    json_result = json.loads(response.content)["items"]


    # Debugging output
    # print("Raw API Response:", data)
    # print("Status Code:", response.status_code)
    # print("Tracks:", tracks)

    for idx, song in enumerate(json_result):
        print(f"{idx+1}. {song['track']['name']}")

    # return render_template('liked.html', tracks=tracks)
    return json_result



def get_recent_ar_tracks(session):
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = get_auth_header(session['access_token'])
    tracks = get_liked_tracks(session)
    
    ar_tracks = [track for track in tracks if is_ar_track(session, track['track'])]

    return render_template('liked.html', tracks=ar_tracks)


def is_ar_track(session, track):
    artist = track['artists'][0]['name']
    # print(artist)
    artist_id = get_artist_id(session, artist)["id"]
    genres = get_genre_by_artist(session, artist_id)
    for genre in genres:
        genre_words = genre.split()
        for word in genre_words:
            if word in AR_GENRES:
                return True
    return False


def get_auth_header(token):
    return {"Authorization": f"Bearer {token}"}

def get_artist_id(session, artist_name):
    url = f'{API_BASE_URL}search'
    headers = get_auth_header(session['access_token'])  # Corrected this line
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query

    try:
        response = requests.get(query_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad HTTP status codes
    except requests.exceptions.RequestException as e:
        print("Failed to fetch artist:", e)
        return jsonify({'error': 'Failed to fetch artist'}), 500

    # print("Status Code:", response.status_code)
    # print("Response Content:", response.content)

    try:
        json_result = response.json()["artists"]["items"]
    except (json.JSONDecodeError, KeyError) as e:
        print("JSON parsing error or key error:", e)
        return jsonify({'error': 'Failed to parse artist data'}), 500

    if len(json_result) == 0:
        print(f"Artist {artist_name} not found")
        return None

    return json_result[0]


def get_genre_by_artist(session, artist_id):
    url = f"{API_BASE_URL}artists/{artist_id}"
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)["genres"]
    return json_result

