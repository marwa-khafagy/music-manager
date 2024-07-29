import json
import requests 
from flask import jsonify, redirect
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
    playlists = json.loads(response.content)['items']

    for idx, playlist in enumerate(playlists):
        print(f"{idx+1}. {playlist['name']}")

    return "hello"; #jsonify(playlists)
    # return (x for x in jsonify(playlists)['items']['name'])
