# Spotify Playlist Manager

This project is an application that lets users log in with their Spotify account to automatically add recently liked tracks of specified genres to a chosen playlist. It interacts with the Spotify Web API to fetch the user's liked tracks, filter them by genre, and add unique tracks to an existing playlist.

## Technologies Used

- **Python**: Backend logic for handling Spotify API requests.
- **Flask**: A lightweight web framework used for handling routes and user sessions.
- **Spotify Web API**: Used to interact with Spotify accounts, playlists, and track data.
- **Bootstrap**: Frontend framework for styling and responsive design.

## Prerequisites

Before starting, ensure you have a [Spotify Developer Account](https://developer.spotify.com/dashboard/login) with an app created.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/spotify-playlist-manager.git
cd spotify-playlist-manager
```

### 2. Create a `.env` file
Create a .env file in the root directory of the project, using `.env.example` as a guide

## Running the Application
To start the app, run the following command
```python
python main.py
```

This will start the application locally at `http://localhost:5000`. Navigate to this URL in your browser. 
Click on the login link to authorize via spotify and start the playlist update process. 

Once the process is complete, you will see a list of tracks that have been added to your playlist. If no new tracks were found, you will be notified accordingly.

## License
This project is licensed under the MIT License.
