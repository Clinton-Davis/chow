from flask import Flask, redirect, render_template, flash, url_for, request, session
import os
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from os import path
import bcrypt
if path.exists("env.py"):
  import env 


app = Flask(__name__)


app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config["MONGO_DBNAME"] = "chowdown"
app.config["SECRET_KEY"] = os.urandom(24)

mongo = PyMongo(app)


@app.route('/')
@app.route('/all_recipe')
def all_recipe():
  if 'username' in session:
    return ' Hi ' + session['username'] + render_template("all_recipes.html",recipes=mongo.db.recipes.find())
  
  #This looks for all the recips in the recipein chowdown.recipes
  return render_template("all_recipes.html",recipes=mongo.db.recipes.find())
  
    
  
 
@app.route('/recipe/<recipe_id>')
def recipe(recipe_id):
  recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})  
  return render_template('recipe.html', recipe=recipe)
  

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
       users = mongo.db.users 
       existing_email = users.find_one({'email': request.form['userEmail']})
      
       if existing_email is None:
            hashpass = bcrypt.hashpw(request.form['userPassword'].encode('utf-8'), bcrypt.gensalt())
            users.insert({
            'name' : request.form['username'].lower(), 
            'email': request.form['userEmail'],
            'password' : hashpass
            })
            session['username'] = request.form['username']
            return redirect(url_for('all_recipe'))
      
       return 'That email already exists, Check the spelling' 
    return render_template('register.html') 


@app.route('/login_page')
def login_page():
  return render_template('login_page.html')


@app.route('/login', methods=['POST'])
def login():
  users = mongo.db.users
  login_user = users.find_one({'email': request.form['userEmail']})
  if login_user:
      if bcrypt.checkpw(request.form['userPassword'].encode('utf-8'), 
                        login_user['password']):
        session['username'] = request.form['username']
        return redirect(url_for('all_recipe'))
  return 'Invalid username or password' +  render_template('login_page.html')
  
  
  
  
  
#  if request.method == 'POST':
#       userEmail = request.form['userEmail']
#        username = request.form['username']
#        login_user = mongo.db.user.find_one({'email': userEmail})
#        session['username'] = username
#        return redirect(url_for('all_recipes' ))
  
    
  
  
        
      
        
        
        
        
       
        
        
        
        
          
        
  


   
    
  
  
  
  
@app.route('/add_recipe')
def add__recipe():
  #check to see if login in
  #if not redirect to login
  return render_template('add_recipe.html')


@app.route('/insert_recipe', methods=['POST'])
def inset_recipe():
    recipe = mongo.db.recipes
    recipe.insert_one(request.form.to_dict())
    return redirect(url_for('all_recipe'))
    

if __name__ == "__main__":
    app.run(host=os.environ.get('IP'),
            port=(os.environ.get('PORT')),
            debug=True)
    