# 
import requests

from datetime import datetime, timedelta
from flask import Flask , redirect, request, session, jsonify

from dotenv import load_dotenv
import os

import urllib.parse

# what is flask seceret key?
# The Flask secret key is a cryptographic key 
# used to encrypt session cookies and other 
# secure data in Flask applications. It is used 
# to provide security and prevent tampering of data.
app = Flask(__name__)
app.secret_key = "fvY2WQ8S-8t9UZ_53BRkrQ"

# To get the global variables from the .env file
load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URL = os.getenv('REDIRECT_URI')
AUTH_URL = os.getenv('AUTH_URL')
TOKEN_URL = os.getenv('TOKEN_URL')
API_BASE_URL = os.getenv('API_BASE_URL')

# root of the flask app
@app.route('/')
def index():
    return "Welcome welcome <a href='/login'>Login</a>"


@app.route('/login')
def login():
    scope = 'user-read-private user-read-email'
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URL,
        'scope': scope, 
        # by defualt it is False
        # setting it to true will make it so that you have to login every time
        'show_dialog': True
    }

    auth_url = f"{AUTH_URL}?{(urllib.parse.urlencode(params))}"

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

        # to make requests to the api
        session['access_token'] = token_info['access_token']
        # to refresh the token
        session['refresh_token'] = token_info['refresh_token']
        # to get the time the token expires
        session['expires_at']  = datetime.now().timestamp() + token_info['expires_in']
    
    # redirect 
    return redirect('/playlists')

@app.route('/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    response = requests.get(f"{API_BASE_URL}me/playlists", headers=headers)
    playlists = response.json()

    return jsonify(playlists)

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

        return redirect('/playlists')
    return ;

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

