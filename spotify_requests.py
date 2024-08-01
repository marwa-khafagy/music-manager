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
