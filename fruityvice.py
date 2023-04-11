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

    #close connection
    conn.close()

def load_data(cur, conn):
    #get data from API
    response = requests.get("https://fruityvice.com/api/fruit/all")
    txt = response.text
    #load json data into python file
    data = json.loads(txt)

    #create genus table
    create_genus_db(data, cur, conn)
    cont_genus_db(data, cur, conn)

    #create family table
    create_family_db(data, cur, conn)
    cont_family_db(data, cur, conn)

    #create fruits table
    create_fruit_db(data, cur, conn)
    continue_loading_fruits(data, cur, conn)

def create_fruit_db(data, cur, conn):
    #create a table named Fruits
    cur.execute("CREATE TABLE IF NOT EXISTS Fruits (id INTEGER PRIMARY KEY, genus INTEGER, family INTEGER, name TEXT, carbs REAL, protein REAL, fat REAL, calories REAL, sugar REAL)")

    #begin loading data into table
    counter = 1
    #loop through json list
    for item in data:
        nutrition = item["nutritions"]
        
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

def continue_loading_fruits(data, cur, conn):
    # continue inserting until end of fruity file
    for i in range(25, len(data)):
        nutrition = data[i]["nutritions"]
        
        #get fruit's genus
        cur.execute("SELECT id FROM Genus WHERE name = ?", (data[i]["genus"],))
        g = cur.fetchone()[0]
        #get fruit's family
        cur.execute("SELECT id FROM Families WHERE name = ?", (data[i]["family"],))
        f = cur.fetchone()[0]

        fruit = (data[i]["id"], g, f, data[i]["name"], nutrition["carbohydrates"], nutrition["protein"], nutrition["fat"], nutrition["calories"], nutrition["sugar"])
        cur.execute("INSERT INTO Fruits VALUES (?,?,?,?,?,?,?,?,?)", fruit)
    
    #commit changes
    conn.commit()

def create_genus_db(data, cur, conn):
    #create a table named Genus
    cur.execute("CREATE TABLE IF NOT EXISTS Genus (id INTEGER PRIMARY KEY, name TEXT)")

    #begin loading data into a table
    #use insert or ignore to get unique
    counter = 1 # <- tracks which ID we are on
    limit =  1 # <- tracks how many are inserted at this time
    for fruit in data:
        cur.execute("INSERT UNIQUE INTO Genus VALUES (?,?)", (counter, fruit["genus"]))
        counter += 1 #how to increment counter only when inserted? or does it not matter?

        limit += 1
        if limit > 25:
            break

    #commit changes
    conn.commit()

def cont_genus_db(data, cur, conn):
    #continue loading values of genuses
    counter = 1
    for i in range(25, len(data)):
        cur.execute("INSERT UNIQUE INTO Genus VALUES (?,?)", (counter, data[i]["genus"]))
        counter += 1 #how to increment counter only when inserted? or does it not matter?

    #commit changes
    conn.commit()

def create_family_db(data, cur, conn):
    #create a table named Families
    cur.execute("CREATE TABLE IF NOT EXISTS Families (id INTEGER PRIMARY KEY, name TEXT)")

    #begin loading data into table
    counter = 1
    limit = 1
    for fruit in data:
        cur.execute("INSERT OR IGNORE INTO Families VALUES (?,?)", (counter, fruit["family"]))
        counter += 1 #how to increment counter only when inserted? or does it not matter?

        limit += 1
        if limit > 25:
            break

    #commit changes
    conn.commit()

def cont_family_db(data, cur, conn):
    #continue loading values of genuses
    counter = 1
    for i in range(25, len(data)):
        cur.execute("INSERT UNIQUE INTO Genus VALUES (?,?)", (counter, data[i]["family"]))
        counter += 1 #how to increment counter only when inserted? or does it not matter?

    #commit changes
    conn.commit()

def calc_data(data, cur, conn):
    #select fruits with the familly "Rosaceae" and determine how many fruits
    #out of total are in that family
    cur.execute("SELECT * FROM Fruits WHERE family = ?", ("Rosaceae",))
    ros_count = len(cur.fetchall())
    cur.execute("SELECT * FROM Fruits")
    total_count = len(cur.fetchall())
    ros_perc = ros_count // total_count * 100

    #join fruits where 

if __name__ == '__main__':
    gather_data()
    


