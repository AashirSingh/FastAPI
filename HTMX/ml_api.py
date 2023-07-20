# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 05:04:58 2023

@author: Administrator
"""
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000/movies_prediction"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["http://127.0.0.1:8000/movies_prediction"],  # Allows all methods
    allow_headers=["http://127.0.0.1:8000/movies_prediction"],  # Allows all headers
)

class model_input(BaseModel):
    IMDB_Rating: float
    Biography: int
    Drama: int
    Thriller: int
    Comedy: int
    Crime: int
    Mystery: int
    History: int
    
#Loading the saved model
movies_model = pickle.load(open("movies_model.sav", "rb"))

df = pd.read_csv("https://github.com/ArinB/MSBA-CA-Data/raw/main/CA05/movies_recommendation_data.csv")


@app.post("/movies_prediction")
def movies_pred(input_data):
    
    #input_data = input_parameters.json()
    input_dictionary = json.loads(input_data)
    
    imdb = input_dictionary["IMDB_Rating"]
    bio = input_dictionary["Biography"]
    dra = input_dictionary["Drama"]
    thr = input_dictionary["Thriller"]
    com = input_dictionary["Comedy"]
    cri = input_dictionary["Crime"]
    mys = input_dictionary["Mystery"]
    his = input_dictionary["History"]
    
    input_list = [imdb, bio, dra, thr, com, cri, mys, his]
    distances, indices = movies_model.kneighbors([input_list])
    print("ml_api line 54: " ,input_list)
    print(input_dictionary)

    movies = []
    for index in indices[0]:
        movies.append(df.iloc[index]["Movie Name"])
        
    return {"Movie Recommendations": movies}

movies_pred(model_input)
        
    
    
    
    
    
    
