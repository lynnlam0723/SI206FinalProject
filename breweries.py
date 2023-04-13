import requests
import os
import sqlite3
import json
import matplotlib
import matplotlib.pyplot as plt


states = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming"
]

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
            cur.execute("""INSERT OR IGNORE INTO Breweries(id, name, state, city, zip_code) VALUES (?, ?, ?, ?, ?)""", 
                        (data["id"], data["name"], data["state"], data["city"], int(data["postal_code"].split('-')[0])))
    conn.commit()

def access_multiple_pages(conn, cur):
    for i in range(1000):
        json_data = set_up_connection(i + 1)
        insert_into_db(conn, cur, json_data)


def calculate_number_per_state(conn, cur):
    result = []
    for state in states:
        cur.execute("SELECT * FROM Breweries WHERE state = ?", (state, ))
        count = int(len(cur.fetchall()))
        result.append(count)
    return result

def create_bar_chart(counts_per_state):
    plt.figure(1)
    plt.barh(states, counts_per_state)
    plt.show()

def print_results_to_file(counts_per_state):
    with open("breweries_per_state", 'w') as f:
        for i in range(50):
            f.write(f"{states[i]}, {counts_per_state[i]}\n")
    

def main():
    conn, cur = set_up_database()
    # create_brew_db(conn, cur)
    # access_multiple_pages(conn, cur)
    counts_per_state = calculate_number_per_state(conn, cur)
    # create_bar_chart(counts_per_state)
    print_results_to_file(counts_per_state)




if __name__ == '__main__':
    main()