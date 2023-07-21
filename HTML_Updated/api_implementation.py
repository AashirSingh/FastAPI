import json
import requests

url = "http://127.0.0.1:8000/prediction"

input_data_for_model = {
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

response = requests.post(url, json=input_data_for_model)

# Check if the request was successful
if response.status_code == 200:
    print(response.json())
else:
    print(f"Request failed with status code: {response.status_code}")
