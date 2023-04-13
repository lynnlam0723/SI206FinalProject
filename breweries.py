import requests
import os
import sqlite3
import json


def set_up_connection(page):
    # get the response from the URL
    url = f"https://api.openbrewerydb.org/v1/breweries?page={page}&per_page=25"
    resp = requests.get(url)
    #load json data into python file
    data = json.loads(resp.text)
    return data



def set_up_database():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+ "breweries.db")
    cur = conn.cursor()
    return (conn, cur)


def create_brew_db(conn, cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS Breweries 
                (id TEXT PRIMARY KEY,
                name TEXT,
                state TEXT, 
                city TEXT,
                zip_code INTEGER,
                UNIQUE(id))""")
    conn.commit()

def insert_into_db(conn, cur, json_data):
    for data in json_data:
        if (data["country"] == "United States"):
            cur.execute("""INSERT OR IGNORE INTO Breweries(id, name, state, zip_code) VALUES (?, ?, ?, ?)""", 
                        (data["id"], data["name"], data["state"], int(data["postal_code"].split('-')[0])))
    conn.commit()

def access_multiple_pages(conn, cur):
    for i in range(50):
        json_data = set_up_connection(i + 1)
        insert_into_db(conn, cur, json_data)


def main():
    conn, cur = set_up_database()
    create_brew_db(conn, cur)
    access_multiple_pages(conn, cur)



if __name__ == '__main__':
    main()