import json
import requests

url = "http://127.0.0.1:8000/movies_prediction"

input_data_for_model = {
    "movie": {
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
}

response = requests.post(url, json=input_data_for_model)

print(response.json())
