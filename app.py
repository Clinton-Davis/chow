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
    return  render_template("all_recipes.html", session_name=session['username'], recipes=mongo.db.recipes.find())
    
    
  #This looks for all the recips in the recipein chowdown.recipes
  return render_template("all_recipes.html",recipes=mongo.db.recipes.find())
  
    
@app.route('/about')
def about():
  return render_template('about.html')
 
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
            flash('You have be successfull registered and are login In', 'success')
            return redirect(url_for('all_recipe'))
      
    flash('That email already exists, Check the spelling', 'warning')
    return render_template('register.html') 


@app.route('/login_page')
def login_page():
  return render_template('login_page.html')


@app.route('/login', methods=['POST','GET'])
def login():
  users = mongo.db.users
  login_user = users.find_one({'email': request.form['userEmail']})
  if login_user:
      if bcrypt.checkpw(request.form['userPassword'].encode('utf-8'), 
                        login_user['password']):
        session['username'] = request.form['username']
        session['logged_in'] = True
        flash('You are now Logged In', 'success')
        return redirect(url_for('all_recipe'))
      
  flash('That is an Inalid username or password', 'warning')
  return render_template('login_page.html')
  
  
@app.route('/add_recipe')
def add_recipe():
  #check to see if login in
    if 'username' in session:
       return  render_template("add_recipe.html", session_name=session['username'])
     
    flash('You Need to be logged in to add a new recipe', 'warning')
    return redirect(url_for('login_page'))
  #if not redirect to login



@app.route('/insert_recipe', methods=['POST'])
def inset_recipe():
    recipe = mongo.db.recipes
    recipe.insert_one(request.form.to_dict())
    flash('You have successfully added your recipe', 'success')
    return redirect(url_for('all_recipe'))
    


@app.route('/delete_recipe/<recipe_id>')
def delete_recipe(recipe_id):
  if 'username' in session:
    recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    if session['username'] == recipe['username']:
      recipe = mongo.db.recipes.remove({'_id': ObjectId(recipe_id)})
      return redirect(url_for('all_recipe'))
  flash('Sorry! Not yours to Delete', 'danger')
  return redirect(url_for('login_page'))   
    
    

@app.route('/edit_recipe/<recipe_id>')
def edit_recipe(recipe_id):
  if 'username' in session:
        recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
        if session['username'] == recipe['username']:
         return render_template('edditrecipe.html', recipe=recipe)  
  flash('Sorry! Not yours to Edit', 'danger')
  return redirect(url_for('login_page')) 
  
  
  
@app.route('/logout')
def logout():
  return redirect(url_for('all_recipe'))
  
if __name__ == "__main__":
    app.run(host=os.environ.get('IP'),
            port=(os.environ.get('PORT')),
            debug=True)
    