from flask import Flask, redirect, request, session, url_for
import random
import string
import requests
import urllib.parse

app = Flask(__name__)
app.secret_key = 'your_secret_key'

client_id = 'YOUR_CLIENT_ID'
redirect_uri = 'http://localhost:8888/callback'

def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

@app.route('/login')
def login():
    state = generate_random_string(16)
    scope = 'user-read-private user-read-email'

    query_params = {
        'response_type': 'code',
        'client_id': client_id,
        'scope': scope,
        'redirect_uri': redirect_uri,
        'state': state
    }
    auth_url = 'https://accounts.spotify.com/authorize?' + urllib.parse.urlencode(query_params)
    return redirect(auth_url)

if __name__ == '__main__':
    app.run(port=8888)
