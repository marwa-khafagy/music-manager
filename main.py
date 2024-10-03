from flask import Flask, redirect, request, session, jsonify, render_template
from datetime import datetime
import os
import urllib.parse
import requests

# for input arguments
import sys 
import spotify_requests

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URL = os.getenv('REDIRECT_URI')

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"

app = Flask(__name__)
app.secret_key = "fvY2WQ8S-8t9UZ_53BRkrQ"

@app.route('/')
def index():
    # if len(sys.argv) != 2:
    #     return "BEEP BOOP no function specified"
    # return "Welcome welcome <a href='/login'>Login</a>"
    return render_template('index.html')


@app.route('/login')
def login():
    scope = 'user-read-private user-read-email user-library-read playlist-modify-public playlist-modify-private'
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URL,
        'scope': scope
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    return redirect(auth_url)


@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URL,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
    
    return redirect('/recent_tracks')


@app.route('/recent_tracks')
def func():
    return spotify_requests.add_recent_tracks(session)

@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

        return redirect('/recent_tracks')
    return ;

@app.route('/BOO')
def boo():
    return "BOOOO"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
