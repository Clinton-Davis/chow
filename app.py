from flask import Flask, redirect, render_template, url_for, request
import os
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from os import path
if path.exists("env.py"):
  import env 


app = Flask(__name__)

app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config["MONGO_DBNAME"] = "chowdown"

mongo = PyMongo(app)


@app.route('/')
@app.route('/get_recipe')
def get_recipe():
  #This looks for all the recips in the recipein chowdown.recipes
    return render_template("recipes.html",recipes=mongo.db.recipes.find())
  
@app.route('/add_recipe')
def add__recipe():
  return render_template('add_recipe.html')

@app.route('/insert_recipe', methods=['POST'])
def inset_recipe():
    recipe = mongo.db.recipes
    recipe.insert_one(request.form.to_dict())
    return redirect(url_for('get_recipe'))
    

if __name__ == "__main__":
    app.run(host=os.environ.get('IP'),
            port=(os.environ.get('PORT')),
            debug=True)