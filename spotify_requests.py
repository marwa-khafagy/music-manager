import json
import requests 
from flask import jsonify, redirect, render_template
from datetime import datetime
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
API_BASE_URL = os.getenv('API_BASE_URL')

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

    data = response.json()
    tracks = data.get('items', [])

    # Debugging output
    # print("Raw API Response:", data)
    print("Status Code:", response.status_code)
    # print("Tracks:", tracks)

    return render_template('liked.html', tracks=tracks)


def get_recent_ar_tracks():
    return;

def is_ar_track(track):
    return;

