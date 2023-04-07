import unittest
import sqlite3
import json
import os
import requests

#format of entries
# "genus": "Malus",
#     "name": "Apple",
#     "id": 6,
#     "family": "Rosaceae",
#     "order": "Rosales", <- omit
#     "nutritions": {
#         "carbohydrates": 11.4,
#         "protein": 0.3,
#         "fat": 0.4,
#         "calories": 52,
#         "sugar": 10.3
#     }
#json is a list of dictionaries

def gather_data():
    #create path for database
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+ "fruit.db")
    cur = conn.cursor()

    #create database
    create_db(cur, conn)

def create_db(cur, conn):
    #get data from API
    response = requests.get("https://fruityvice.com/api/fruit/all")
    txt = response.text
    #load json data into python file
    data = json.loads(txt)
    #create a table named Fruits
    cur.execute("CREATE TABLE Fruits (id INTEGER PRIMARY KEY, genus TEXT, family TEXT, name TEXT, carbs INT, protein INT, fat INT, calories INT, sugar INT)")

    #begin loading data into table
    #loop through json list
    for item in data:
        nutrition = item["nutrition"]
        fruit = (item["id"], item["genus"], item["family"], item["name"], nutrition["carbohydrates"], nutrition["protein"], nutrition["fat"], nutrition["calories"], nutrition["sugar"])
        cur.execute("INSERT INTO Fruits VALUES (?,?,?,?,?,?,?,?,?)", fruit)

#def calc_data():





