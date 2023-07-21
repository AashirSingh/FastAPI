import json
import requests

url = "http://127.0.0.1:8000/prediction"

# Define the payload for the post request according to the Movie model
movie = {
    "imdb_rating": 8.0,
    "genres": {
        "bio": False,
        "drama": True,
        "thriller": True,
        "comedy": True,
        "crime": True,
        "mystery": False,
        "history": False
    }
}

# Make a post request to the server
response = requests.post(url, json=movie)

# If the request was successful, print the returned movie names
if response.status_code == 200:
    predicted_movie_names = response.json()['prediction']
    print(f"Predicted Movie Names: {predicted_movie_names}")
else:
    print(f"Request failed with status code: {response.status_code}")
