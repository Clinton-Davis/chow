import os
import datetime
import bcrypt
from flask import Flask, redirect, render_template, flash, url_for, request, session
from flask_pymongo import PyMongo
from flask_ckeditor import CKEditor
from bson.objectid import ObjectId
from os import path
if path.exists("env.py"):
  import env 


app = Flask(__name__)


app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config["MONGO_DBNAME"] = "chowdown"
app.config["SECRET_KEY"] = os.urandom(24)

mongo = PyMongo(app)
CKEditor(app)

@app.route('/')
@app.route('/all_recipe')
def all_recipe():
  #If there is a user logged: Username is printed in the Nav
  if 'username' in session:
    #Puts the resipe in order Newest to oldest
    return  render_template("all_recipes.html", 
                            session_name=session['username'], 
                            recipes=mongo.db.recipes.find().sort("_id", -1)) 
  #Puts the resipe in order Newest to oldest but with out the login username
  return render_template("all_recipes.html",
                         recipes=mongo.db.recipes.find().sort("_id", -1))
  

  

@app.route('/category', methods=['POST','GET'])   
def category():
  recipes = mongo.db.recipes
  #This makes sure a catergory is selected
  if  request.form.get ('category_search') == None:
    return redirect('all_recipe')
  if 'username' in session:
    #This displays the categorys choisen by user
    return  render_template("all_recipes.html", 
                            session_name=session['username'],
                            recipes=recipes.find({'category': request.form.get ('category_search')}))
  return  render_template("all_recipes.html", 
                          recipes=recipes.find({'category': request.form.get ('category_search')}))
    
    
@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/contact')
def contact():
  return render_template('contact.html')
 
 #This sends the choise recipe to the recipe with a full list of details
@app.route('/recipe/<recipe_id>')
def recipe(recipe_id):
  recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})  
  if 'username' in session:
    return render_template('recipe.html',session_name=session['username'], recipe=recipe)
  return render_template('recipe.html', recipe=recipe)
  

#registering route
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
      #Looking for existing users using there emails, emails are more uniue
       users = mongo.db.users 
       existing_email = users.find_one({'email': request.form['userEmail']})
       if existing_email is None:
            hashpass = bcrypt.hashpw(request.form['userPassword'].encode('utf-8'), bcrypt.gensalt())
            users.insert({
            'name' : request.form['username'].lower(), 
            'email': request.form['userEmail'].lower(),
            'password' : hashpass
            })
            session['username'] = request.form['username']
            flash('Hello ' + session['username'] + ' You have be successfull registered and are login In', 'success')
            return redirect(url_for('all_recipe'))
      
    flash('That email already exists, Check the spelling', 'warning')
    return render_template('register.html') 




@app.route('/login', methods=['POST','GET'])
def login():
  if request.method == 'POST':
      users = mongo.db.users
      login_user = users.find_one({'email': request.form['userEmail']})
      if login_user:
        if bcrypt.checkpw(request.form['userPassword'].encode('utf-8'), 
                        login_user['password']):
          session['username'] = request.form['username']
          session['logged_in'] = True
          flash('Welcome Back ' + session['username'] + ' You are now Logged In', 'success')
          return redirect(url_for('all_recipe'))    
        flash('That is an Inalid Username or Password', 'warning')
        return render_template('login_page.html')
  return render_template('login_page.html')
  
  
  #addes todays date in day/month/year format
  #check to see if login in
  #if not redirect to login
@app.route('/add_recipe',methods=['POST','GET'])
def add_recipe():
  today = datetime.datetime.now().strftime('%d/%m/%Y')
  if 'username' in session:
      if request.method == 'POST':
          recipes = mongo.db.recipes
          recipes.insert_one(request.form.to_dict(),)
          flash('You have Successfully Added a Recipe', 'success')
          return redirect(url_for('all_recipe'))
      return  render_template("add_recipe.html", session_name=session['username'], date_added=today)
  flash('You Need to be Logged In to Add a New Recipe', 'warning')
  return redirect(url_for('login'))

#Inserts New recipe

    
    


"""This Route checks to see if:
1. If User is in session: 
    True:-continue to get ID
    False:-redirect to Login: Returns out.
2. Get's the ID of the recipe
3. If session name matches the user that posted the recipe
    True:-removes recipe with ID and redirects to all_recipes
    False:-redirect to Login: Returns out."""
    
@app.route('/delete_recipe/<recipe_id>')
def delete_recipe(recipe_id):
  if 'username' in session:
    recipes = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    if session['username'] == recipes['username']:
      recipe = mongo.db.recipes.remove({'_id': ObjectId(recipe_id)})
      return redirect(url_for('all_recipe'))
    flash('Sorry! You have to Login first', 'danger')
    return redirect(url_for('login_page'))   
  flash('Sorry! You have to Login first', 'danger')
  return redirect(url_for('login_page')) 
    
    
"""This Route checks to see if:
1. If User is in session: 
    True:-continue to get ID
    False:-redirect to Login: return out.
2. Get's the ID of the recipe
3. If session name matches the user that posted the recipe
    True:-Check to see if method is POST #4
    Flase:- Render edit_recipe template: return out
4.  If method is POST create recipes variable and update recipe, Flash Success
    redirect to all_recipe: return out"""
    
@app.route('/edit_recipe/<recipe_id>', methods=['POST','GET'])
def edit_recipe(recipe_id): 
    if 'username' in session: #1
          recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)}) #2
          if session['username'] == recipe['username']: #3
              if request.method == 'POST': #4
                 recipes = mongo.db.recipes
                 recipes.update({'_id': ObjectId(recipe_id)},                          
                  {'username' : request.form.get('username'),
                  'chef': request.form.get('chef'),
                  'recipe_name' : request.form.get('recipe_name'),
                  'descrition' : request.form.get('descrition'),
                  'category': request.form.get('category'),
                  'servings' : request.form.get('servings'),
                  'cooking_time' : request.form.get('cooking_time'),
                  'dish_image' : request.form.get('dish_image'),
                  'ingredients' : request.form.get('ingredients'),
                  'cooking_method' : request.form.get('cooking_method'),
                  'date_added': request.form.get('date_added')})  
                 flash(' You have Successfully Updated Your Recipe', 'success')
                 return redirect(url_for('all_recipe', recipe=recipe))
              return render_template('edit_recipe.html',session_name=session['username'], recipe=recipe)#3      
    flash('Sorry! You have to Login First', 'danger')
    return redirect(url_for('login_page')) #1


"""This Route take the session username and 
  1. changes it to none
  2. makes the Loggin_in = False"""
@app.route('/logout')
def logout():
   # remove the username from the session if it's there
    session.pop('username', None)
    session['logged_in'] = False
    return redirect(url_for('all_recipe'))
  
if __name__ == "__main__":
    app.run(host=os.environ.get('IP'),
            port=(os.environ.get('PORT')),
            debug=True)
    