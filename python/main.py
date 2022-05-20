import os
import json
import sqlite3
import hashlib
import logging
import pathlib
import sys
#from numpy import integer
import requests
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

#connect to the database
mycon = sqlite3.connect('mercari.sqlite3',check_same_thread=False)
c = mycon.cursor()
# c.execute("DROP TABLE items")
# c.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name STRING, category STRING, image STRING);")
mycon.commit()
#close the connection
mycon.close()

#function to has the image in path spcifies
def hash_image(image):
    #error message if image path doesnt end with .jpg
    if not image.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    #open the file as read binary and hash 
    with open(image,"rb") as f:
        bytes = f.read() # read entire file as bytes
        readable_hash = hashlib.sha256(bytes).hexdigest();
        f.close()

    #return the hashed image
    return (f'{readable_hash}.jpg')
        

@app.get("/")
def root():
    return {"message": "Hello, world!"}
    
data =[];
data1 ={"items": data}
@app.post("/items")
def add_item(name: str = Form(...),category: str = Form(...), image: str = Form(...)):
    mycon = sqlite3.connect('mercari.sqlite3',check_same_thread=False)
    c = mycon.cursor()
    hashed_image = hash_image(image)
    c.execute("INSERT INTO items (name,category,image) VALUES (?,?,?)",(name,category,hashed_image))
    mycon.commit()
    mycon.close()
    #  data.append({"name": name, "category": category})
    #  with open('items.json', "w") as file:
    #      json.dump(data1, file)
    
    logger.info(f"Receive item: {name}, category: {category}, image: {hashed_image}" )
    return {"message": f"item received: {name}, category: {category},, image: {hashed_image}"}

# @app.get("/search?keyword={search_word}")
# def get_search(search_word):
#     
     
# @app.get("/items")
# def get_item():
#     return c.execute("SELECT * FROM items");

@app.get("/items")
def get_item():
    mycon = sqlite3.connect('mercari.sqlite3',check_same_thread=False)
    mycon.row_factory = sqlite3.Row
    c = mycon.cursor()
    rows = c.execute("SELECT * FROM items").fetchall()
    mycon.commit()
    mycon.close()

    data = []    
    for row in rows:
        columns = row.keys()
        data.append({key: row[key] for key in columns})

    return {"items": data}
    # with open('items.json', "r") as file:
    #     data1 = json.load(file).``
    # return data1



@app.get("/search")
def search_items(keyword: str):
    mycon = sqlite3.connect('mercari.sqlite3',check_same_thread=False)
    mycon.row_factory = sqlite3.Row
    c = mycon.cursor()
    rows = c.execute("SELECT * FROM Items WHERE name LIKE ? OR category LIKE ?",(keyword,keyword)).fetchall()
    mycon.commit()
    mycon.close()

    data = []    
    for row in rows:
        columns = row.keys()
        data.append({key: row[key] for key in columns})
    return {"items": data}


@app.get("/items/{item_id}")
def get_item_id(item_id):
    mycon = sqlite3.connect('mercari.sqlite3',check_same_thread=False)
    mycon.row_factory = sqlite3.Row
    c = mycon.cursor()
    rows = c.execute("SELECT name,category,image FROM items WHERE id LIKE ?",(item_id,)).fetchall()
    mycon.commit()
    mycon.close()

    data = []    
    for row in rows:
        columns = row.keys()
        data.append({key: row[key] for key in columns})

    return data



@app.get("/image/{image_filename}")
async def get_image(image_filename):
    # Create image path
    image = images / image_filename

