import sqlite3
import json
import os
import requests

def gather_data():
    #create path for database
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+ "beer.db")
    cur = conn.cursor()

    #create table
    cur.execute("CREATE TABLE IF NOT EXISTS Beers VALUES (id INTEGER PRIMARY KEY, name TEXT, abv INTEGER, ph INTEGER, contributed_by_id INTEGER)")

    #load in data
    load_data("", cur, conn)
    load_data("?page=26&per_page=25", cur, conn)
    load_data("?page=51&per_page=25", cur, conn)
    load_data("?page=76&per_page=25", cur, conn)

    #close connection
    conn.close()

def load_data(page_num, cur, conn):
    #get data from API
    url = "https://api.punkapi.com/v2/beers" + page_num
    response = requests.get("url")
    txt = response.text
    #load json data into python file
    data = json.loads(txt) #list of dicts

    #create contributer table
    create_contributed_db(data, cur, conn)

    #data loading in: id, name, abv, ph, contributed by
    for beer in data:
        cur.execute("SELECT id FROM Contributer WHERE name = ?", (beer["contributed_by"],))
        b = (beer["id"], beer["name"], beer["abv"], beer["ph"], cur.fetchone()[0])
        cur.execute("INSERT INTO Beers VALUES (?,?,?,?,?)", b)

    #commit changes
    conn.commit()

def create_contributed_db(data, cur, conn):
    #create the table
    cur.execute("CREATE TABLE IF NOT EXISTS Contributers VALUES (id INTEGER PRIMARY KEY, name TEXT)")

    #load names
    counter = 1
    for item in data:
        cur.execute("INSERT OR IGNORE INTO Contributers VALUES (?,?)", (counter, item["contributed_by"]))
        counter += 1

    #commit changes
    conn.commit()

if __name__ == '__main__':
    gather_data()