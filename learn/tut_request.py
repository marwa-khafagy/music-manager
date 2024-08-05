from dotenv import load_dotenv
import os
import base64
import json  # Add this line to import the json module
# allows us to send post requests
from requests import post, get

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

def get_token():
    auth_str = f"{client_id}:{client_secret}"
    auth_bytes = auth_str.encode("utf-8")
    # inside the st it returns a base64 object
    auth_b64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": f"Bearer {token}"}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query

    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print(f"Artist {artist_name} not found")
        return
    return json_result[0]

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = get_auth_header(token)
    query = "?market=US"
    query_url = url + query

    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

def get_genre_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["genres"]
    return json_result
# not working
def get_me(token):
    url = "https://api.spotify.com/v1/search?q=tag%3AArabic&type=track&limit=50"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    return json.loads(result.content)


def get_last_50(token):
    url = f"https://api.spotify.com/v1/me/tracks?limit=50"
    headers = get_auth_header(token)
    query = "?market=US"
    query_url = url + query

    result = get(query_url, headers=headers)
    return json.loads(result.content)["items"]

token = get_token()

result = search_for_artist(token, "Haifa Wehbe")
artist_id = result["id"]
# songs = get_songs_by_artist(token, artist_id)

genre = get_genre_by_artist(token, artist_id)

# for idx, song in enumerate(songs):
#     print(f"{idx+1}. {song['name']}")

tracks = get_last_50(token)

for idx, song in enumerate(tracks):
    print(f"{idx+1}. {song['name']}")

# print(genre)

# print('\n\n')

me = get_me(token)['tracks']['items']

# for idx, song in enumerate(me):
#     print(f"{idx+1}. {song['name']}")
print()
# print(me)

