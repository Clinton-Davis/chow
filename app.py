from flask import Flask, redirect, render_template, flash, url_for, request, session
import os
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from os import path
from flask_bcrypt import Bcrypt
if path.exists("env.py"):
  import env 


app = Flask(__name__)
bcrypt = Bcrypt(app)

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
  
""" Reg: checks to see if a post is bing made 
    check to see if a user already exists
    hashes a password
    inserts data in users.db 
    redirects to home(all_recipe) or back to reg if user exists"""
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
       users = mongo.db.users 
       existing_user = users.find_one({'username': request.form['username']})
       password = request.form['userPassword']
       username = request.form['username']
       
       if password == '' or username == '':
         error = 'Please fill in Username and Password'
         return render_template('register.html', error=error)
       
       
       if existing_user is None:
         users.insert({
           'username' : request.form['username'].lower(), 
           'email': request.form['userEmail'],
           'password' : request.form['userPassword']
           })
         session['username'] = request.form['username']
         return redirect(url_for('all_recipe'))
      
       return 'That name already exists, try another' + render_template('reg.html')
    return render_template('register.html') 
     
  

@app.route('/login', methods=['POST','GET'])
def login():
  if request.method == 'POST':
        userEmail = request.form['userEmail']
        username = request.form['username']
        login_user = mongo.db.user.find_one({'email': userEmail})
        session['username'] = username
        return redirect(url_for('all_recipes' ))
  else:
    return 'Invalid username email'
  
  return redirect(url_for(reg))
        
      
        
        
        
        
       
        
        
        
        
          
        
  


   
    
  
  
  
  
@app.route('/add_recipe')
def add__recipe():
  #check to see if login in
  if 'username' in session:
    return render_template('add_recipe.html')
  #if not redirect to login
  return render_template('/login.html')


@app.route('/insert_recipe', methods=['POST'])
def inset_recipe():
    recipe = mongo.db.recipes
    recipe.insert_one(request.form.to_dict())
    return redirect(url_for('all_recipe'))
    

if __name__ == "__main__":
    app.run(host=os.environ.get('IP'),
            port=(os.environ.get('PORT')),
            debug=True)
    