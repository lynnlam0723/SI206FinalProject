import sqlite3
import json
import os
import requests
import matplotlib
import matplotlib.pyplot as plt

def gather_data(cur, conn):
    #create table
    cur.execute("CREATE TABLE IF NOT EXISTS Beers (id INTEGER PRIMARY KEY, name TEXT, abv REAL, ph REAL, contributed_by_id INTEGER)")

    #load in data
    load_data("", cur, conn)
    load_data("?page=2", cur, conn)
    load_data("?page=3", cur, conn)
    load_data("?page=4", cur, conn)
    load_data("?page=5", cur, conn)

    return cur, conn

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
        cur.execute("INSERT OR IGNORE INTO Beers VALUES (?,?,?,?,?)", b)

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

def visualization(data):
    plt.figure(1)

    #create x and y values

    #sort by increasing abv
    data.sort(key = lambda x: x[1])

    #x = id by abv, y = id by pH
    # abvs = create_axis_values(data, 1)
    # phs = create_axis_values(data, 2)

    x_vals, y_vals = create_axes(data)

    #create and show scatterplot
    plt.plot(x_vals, y_vals)
    plt.show()
    #no relation :/

    #plot max abvs
    data.sort(key = lambda x: x[1], reverse=True)
    names = [data[0][3], data[1][3], data[2][3], data[3][3], data[4][3]]
    abvs = [data[0][1], data[1][1], data[2][1], data[3][1], data[4][1]]
    plt.barh(names, abvs)
    plt.show()

def create_axes(data):
    #data is sorted by increasing abv value
    x = list()
    y = list()
    for beer in data:
        x.append(beer[1])
        y.append(beer[2])

    return x, y
    
def create_axis_values(data, idx):
    axis = list()
    for beer in data:
        if beer[idx] not in axis:
            axis.append(beer[idx])
    return axis

def data_calcs(cur, conn):
    #join beers with a ph over 4.4 and abv over 8

    #ph over 4.4
    cur.execute("CREATE TABLE IF NOT EXISTS pHOver4 (id INTEGER PRIMARY KEY, name TEXT, abv REAL, ph REAL, contributed_by_id INTEGER)")
    cur.execute("SELECT * FROM Beers WHERE ph > 4.3")
    data = cur.fetchall()
    for beer in data:
        b = (beer[0], beer[1], beer[2], beer[3], beer[4])
        cur.execute("INSERT OR IGNORE INTO pHOver4 VALUES (?,?,?,?,?)", b)

    #join tables
    #format: id, abv, ph
    cur.execute("SELECT Beers.id, Beers.abv, pHOver4.ph, pHOver4.name FROM Beers JOIN pHOver4 ON Beers.abv > 8.0 AND Beers.id = pHOver4.id AND Beers.abv < 20.0")
    beers = cur.fetchall()

    conn.commit()

    #visualize data
    visualization(beers)

    return cur, conn

def main():
    #create path for database
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+ "beer.db")
    cur = conn.cursor()

    cur, conn = gather_data(cur, conn)
    cur, conn = data_calcs(cur, conn)
    conn.close()

if __name__ == '__main__':
    main()