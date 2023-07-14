# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 05:33:32 2023

@author: Administrator
"""

import json
import requests

url = "http://127.0.0.1:8000/movies_prediction"



input_data_for_model = {
    
    "IMDB_Rating" : 8.0,
    "Biography" : 0,
    "Drama" : 1,
    "Thriller" : 1,
    "Comedy" : 1,
    "Crime" : 1,
    "Mystery" : 0,
    "History" : 0
    
    }

response = requests.post(url, json = input_data_for_model)

print(response.json())
