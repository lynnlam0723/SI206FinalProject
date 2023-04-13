import sqlite3
import json
import os
import requests

def gather_data(cur, conn):
    #create table
    cur.execute("CREATE TABLE IF NOT EXISTS Beers (id INTEGER PRIMARY KEY, name TEXT, abv REAL, ph REAL, contributed_by_id INTEGER)")

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
    response = requests.get(url)
    txt = response.text
    #load json data into python file
    data = json.loads(txt) #list of dicts

    #create contributer table
    create_contributed_db(data, cur, conn)

    #data loading in: id, name, abv, ph, contributed by
    for beer in data:
        cur.execute("SELECT id FROM Contributers WHERE name = ?", (beer["contributed_by"],))
        b = (beer["id"], beer["name"], beer["abv"], beer["ph"], cur.fetchone()[0])
        cur.execute("INSERT INTO Beers VALUES (?,?,?,?,?)", b)

    #commit changes
    conn.commit()

def create_contributed_db(data, cur, conn):
    #create the table
    cur.execute("CREATE TABLE IF NOT EXISTS Contributers (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")

    #load names
    for item in data:
        cur.execute("SELECT MAX(id) FROM Contributers")
        counter = 1
        if cur.fetchone()[0] is not None:
            counter = cur.fetchone()
        cur.execute("INSERT OR IGNORE INTO Contributers VALUES (?,?)", (counter, item["contributed_by"]))

    #commit changes
    conn.commit()

def data_calcs(cur, conn):
    #select beers with a ph under 4
    cur.execute("SELECT name FROM Beers WHERE ph < 4.0")


if __name__ == '__main__':
    #create path for database
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+ "beer.db")
    cur = conn.cursor()

    gather_data(cur, conn)