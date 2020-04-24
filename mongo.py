import pymongo
import os
from os import path
if path.exists("env.py"):
  import env 

#This is the mongodb get db.-=-=-=--=-=-
#app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
#app.config["MONGO_DBNAME"] = "task_manager"
MONGO_URI =os.environ.get("MONGO_URI")
DBS_NAME = "chowdown"
COLLECTION_NAME = "recipes"


def mongo_connect(url):
    try:
        conn = pymongo.MongoClient(url)
        print("Mongo is connected!")
        return conn
    except pymongo.errors.ConnectionFailure as e:
        print("Could not connect to MongoDB: %s") % e       
#-=-=----=-=-=--=---=-=-=-=-=-=--=-=-=-=-=
conn = mongo_connect(MONGO_URI)

coll = conn[DBS_NAME][COLLECTION_NAME]

documents = coll.find()
for doc in documents:
    print(doc)