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

    #load data and create databases
    load_data(cur, conn)

def load_data(cur, conn):
    #get data from API
    response = requests.get("https://fruityvice.com/api/fruit/all")
    txt = response.text
    #load json data into python file
    data = json.loads(txt)

    #create genus table
    create_genus_db(data, cur, conn)
    #create family table
    create_family_db(data, cur, conn)
    #create full fruits table
    create_fruit_db(data, cur, conn)

def create_fruit_db(data, cur, conn):
    #create a table named Fruits
    cur.execute("CREATE TABLE Fruits (id INTEGER PRIMARY KEY, genus INTEGER, family INTEGER, name TEXT, carbs REAL, protein REAL, fat REAL, calories REAL, sugar REAL)")

    #begin loading data into table
    counter = 0
    #loop through json list
    for item in data:
        nutrition = item["nutrition"]
        
        #get fruit's genus
        cur.execute("SELECT id FROM Genus WHERE name = ?", (item["genus"],))
        g = cur.fetchone()[0]
        #get fruit's family
        cur.execute("SELECT id FROM Families WHERE name = ?", (item["family"],))
        f = cur.fetchone()[0]

        fruit = (item["id"], g, f, item["name"], nutrition["carbohydrates"], nutrition["protein"], nutrition["fat"], nutrition["calories"], nutrition["sugar"])
        cur.execute("INSERT INTO Fruits VALUES (?,?,?,?,?,?,?,?,?)", fruit)
        
        #may change lol
        #stop loading after 25 values
        #idk if this is what they meant
        counter += 1
        if counter > 25:
            break
    
    #commit changes
    conn.commit()

def create_genus_db(data, cur, conn):
    #create a table named Genus
    cur.execute("CREATE TABLE Genus (id INTEGER PRIMARY KEY, name TEXT)")

    #begin loading data into a table
    #use insert or ignore to get unique
    counter = 1 # <- tracks which ID we are on
    for fruit in data:
        cur.execute("INSERT OR IGNORE INTO Genus VALUES (?,?)", (counter, fruit["genus"]))
        counter += 1 #how to increment counter only when inserted? or does it not matter?

    #commit changes
    conn.commit()

def create_family_db(data, cur, conn):
    #create a table named Families
    cur.execute("CREATE TABLE Families (id INTEGER PRIMARY KEY, name TEXT)")

    #begin loading data into table
    counter = 1
    for fruit in data:
        cur.execute("INSERT OR IGNORE INTO Families VALUES (?,?)", (counter, fruit["family"]))
        counter += 1 #how to increment counter only when inserted? or does it not matter?

    #commit changes
    conn.commit()

#def calc_data():





