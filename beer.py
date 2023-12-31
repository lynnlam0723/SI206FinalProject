import sqlite3
import json
import os
import requests
import matplotlib
import matplotlib.pyplot as plt

def gather_data(cur, conn):
    #create table
    cur.execute("""CREATE TABLE IF NOT EXISTS Beers (id INTEGER PRIMARY KEY, name TEXT, 
                 abv REAL, ph REAL, contributed_by_id INTEGER)""")

    #load in data
    cur.execute("SELECT * FROM Beers")
    count = len(cur.fetchall())
    if count == 0:
        load_data("", cur, conn)
    elif count < 26:
        load_data("?page=2", cur, conn)
    elif count < 51:
        load_data("?page=3", cur, conn)
    elif count < 76:
        load_data("?page=4", cur, conn)
    else:
        load_data("?page=5", cur, conn)

    return cur, conn

def create_contributed_db(data, cur, conn):
    #create the table
    cur.execute("""CREATE TABLE IF NOT EXISTS Contributers
                 (id INTEGER PRIMARY KEY, name TEXT UNIQUE)""")

    #load names
    for item in data:
        cur.execute("SELECT MAX(id) FROM Contributers")
        counter = 1
        if cur.fetchone()[0] is not None:
            counter = cur.fetchone()
        cur.execute("INSERT OR IGNORE INTO Contributers VALUES (?,?)", 
                    (counter, item["contributed_by"]))

    #commit changes
    conn.commit()

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
        #CHANGE TABLE NAME HERE
        cur.execute("SELECT id FROM Contributers WHERE name = ?",
                     (beer["contributed_by"],))
        b = (beer["id"], beer["name"], beer["abv"], beer["ph"], cur.fetchone()[0])
        cur.execute("INSERT OR IGNORE INTO Beers VALUES (?,?,?,?,?)", b)

    #commit changes
    conn.commit()

def data_calcs(cur, conn):
    #join beers with a ph over 4.4 and abv over 8
    #ph over 4.4
    cur.execute("""CREATE TABLE IF NOT EXISTS pHOver4 (id INTEGER PRIMARY KEY, 
                name TEXT, abv REAL, ph REAL, contributed_by_id INTEGER)""")
    cur.execute("SELECT * FROM Beers WHERE ph > 4.3")
    data = cur.fetchall()
    for beer in data:
        b = (beer[0], beer[1], beer[2], beer[3], beer[4])
        cur.execute("INSERT OR IGNORE INTO pHOver4 VALUES (?,?,?,?,?)", b)

    #format: id, abv, ph, name
    cur.execute("""SELECT Beers.id, Beers.abv, pHOver4.ph, pHOver4.name FROM Beers 
                JOIN pHOver4 ON Beers.abv > 8.0 AND Beers.id = pHOver4.id""")
    beers = cur.fetchall()
    conn.commit()

    #visualize data
    beers.sort(key = lambda x: x[1], reverse=True)
    visualization(beers)

    #calculate average ABV value for beers with a pH at least 4.4
    totalABV = 0
    count = 0
    for beer in beers:
        #list of tuples
        totalABV += beer[2]
        count += 1
    averageABV = totalABV // count
    write_calcs(averageABV)

    return cur, conn

def write_calcs(averageABV):
    with open("beers.txt", 'w', encoding="utf-8-sig") as f:
        f.write("Average ABV Value for Beers with a pH Value of at least 4.4:\n")
        f.write(f"Mean: {averageABV} milliliters of ethanol per 100 milliliters of beer")

def visualization(data):
    #plot max abvs
    #data already sorted
    ax = plt.subplot()
    names = [data[0][3], data[1][3], data[2][3], data[3][3], data[4][3]]
    abvs = [data[0][1], data[1][1], data[2][1], data[3][1], data[4][1]]
    ax.set_xlabel("Alcohol by Volume (mL by 100 mL)")
    ax.set_ylabel("Names")
    ax.set_title("Beers with the Highest ABV Values")
    ax.barh(names, abvs, color='green')
    plt.show()

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