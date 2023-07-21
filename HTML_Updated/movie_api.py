from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pickle
import numpy as np

class Genre(BaseModel):
    bio: bool
    drama: bool
    thriller: bool
    comedy: bool
    crime: bool
    mystery: bool
    history: bool

class Movie(BaseModel):
    imdb_rating: float
    genres: Genre

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Load your trained model when the application starts
model = pickle.load(open("movies_model.sav", "rb"))

@app.post("/prediction")
async def predict_movie(movie: Movie):
    # Print values
    print(f"IMDB Rating: {movie.imdb_rating}")
    print(f"Genres:")
    print(f"  Bio: {movie.genres.bio}")
    print(f"  Drama: {movie.genres.drama}")
    print(f"  Thriller: {movie.genres.thriller}")
    print(f"  Comedy: {movie.genres.comedy}")
    print(f"  Crime: {movie.genres.crime}")
    print(f"  Mystery: {movie.genres.mystery}")
    print(f"  History: {movie.genres.history}")

    # Prepare the data in the format your model expects
    data = [
        movie.imdb_rating,
        int(movie.genres.bio),
        int(movie.genres.drama),
        int(movie.genres.thriller),
        int(movie.genres.comedy),
        int(movie.genres.crime),
        int(movie.genres.mystery),
        int(movie.genres.history),
    ]

    # Use the model to make a prediction
    distances, indices = model.kneighbors([data])

    # Return the prediction
    return {"prediction": indices[0].tolist()} 
