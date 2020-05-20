import os
import datetime
import bcrypt
import smtplib
from flask import Flask, redirect, render_template, flash, url_for, request, session, abort
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

""" 
All Recipe (Home Route)
    1. Get today datetime in string formate (for future features)
    2. check to see if user is in sessions
       True: - renders template and passes session user to session_name 
              todays string and sorts the collection in order newest to oldest
        False: - renders template with out session or date and still orders the collection the same way"""
@app.route('/')
@app.route('/all_recipe')
def all_recipe():
  today =  datetime.datetime.now().strftime('%d/%m/%y')
  #If there is a user logged: Username is printed in the Nav
  if 'username' in session:
    #Puts the resipe in order Newest to oldest
    return  render_template("all_recipes.html", 
                            session_name=session['username'], 
                            today=today,
                            recipes=mongo.db.recipes.find().sort("_id", -1)) 
  #Puts the resipe in order Newest to oldest but with out the login username
  return render_template("all_recipes.html",
                         recipes=mongo.db.recipes.find().sort("_id", -1))
  
  
"""
Category Route
    1. Creates variable for collection
    2. Creats a variable for get.form
    3. checks to see if any category has been chosen
       Ture: None have been choosen -redircts to all recips 
    4. False: one has been choosen
    5. check to see if is categorys or chef or myrecipes
    6. if chef is chosen redirct to chef route: return out
       else if Servings is chosen redirects to servings.
       else if myrecipes is chosen redirct to myrecipes route: return out
    7. check to see if user is in session
    8. True render template all recipes with username and recipe quary
        with category order from newest to oldest
       """
@app.route('/category', methods=['POST','GET'])   
def category():
  recipes = mongo.db.recipes
  cat_search =  request.form.get ('category_search')
  if  cat_search == None:
    return redirect('all_recipe')
  
  if cat_search == "chef":
    return redirect('chef')
  elif cat_search == "myrecipes":
    return redirect('myrecipes')
  elif cat_search == "servings":
    return redirect('servings')
  if 'username' in session:
    #This displays the categorys choisen by user
      return  render_template("all_recipes.html", 
                            session_name=session['username'],
                            recipes=recipes.find({'category': cat_search}).sort([('category', -1),("_id", -1)]))
  return  render_template("all_recipes.html", 
                          recipes=recipes.find({'category': cat_search}).sort([('category', -1),("_id", -1)]))


"""
 Chefs Route
    finds all the chef and orders them alphabeticailly """
@app.route('/chef')
def chef():
  if 'username' in session:
    return  render_template("all_recipes.html", 
                            session_name=session['username'], 
                            recipes=mongo.db.recipes.find().sort("chef", 1)) 
  return render_template("all_recipes.html",
                         recipes=mongo.db.recipes.find().sort("chef", 1))

"""
 Servings Route
    finds all the recipes serving size and orders them in ascending """
@app.route('/servings')
def servings():
  if 'username' in session:
    return  render_template("all_recipes.html", 
                            session_name=session['username'], 
                            recipes=mongo.db.recipes.find().sort("servings", 1)) 
  return render_template("all_recipes.html",
                         recipes=mongo.db.recipes.find().sort("servings", 1))

  
"""
My recipes 
    Finds all the recipes that the user has posted"""
@app.route('/myrecipes')
def myrecipes():
   session_name = session['username']
   return  render_template("all_recipes.html", 
                            session_name=session['username'], 
                            recipes=mongo.db.recipes.find({'username': session_name }))
  
   
"""
Renders About Template """
@app.route('/about')
def about():
  return render_template('about.html')

"""
Contact Email Routes 
  1. Checks to see it its a POST Reuest: - False:-Render template Return Out 
  2. True- create Varaibles for Emailers Name/address/message
  3. Create Viarable for the time of submission
  4. Inserts Emailers name/address/message/submission time- into email_inbox collection
  5. Line 81/82 Creating a Subject and Text Varaibles for the email
  6. Creating the message Variable and formating to emails
  7. Define Server and Port (gmails and Port 587)
  8. Start email Server
  9. Login into admin email address
  10. Login to admin email and email user, with message
  11. Quit Server
  12. Return to all_recipes and Return out"""
@app.route('/contact_email', methods=['POST','GET'])
def contact_email():
  if request.method == 'POST':                        #1
    name = request.form.get("name")                   #2
    email_address = request.form.get("email_address") #2
    user_message = request.form.get("user_message")   #2
    message_time = datetime.datetime.now()            #3
    new_emails = mongo.db.email_inbox                 #4
    new_emails.insert({
      'name' : name,
      'email' : email_address,
      'msg' : user_message,
      'sub_time': message_time
    })
    #Dealing wih the emailing
    SUBJECT = "Regarding your Message to Chow"
    TEXT = "Hello " + name + "\n" + "Thank you for getting in touch, Your message is logged and we will be in touch with you soon.\nThank you, and have a good Day." + "\n" + "Chow"  
    message = 'Subject: {}\n\n{}' .format(SUBJECT, TEXT)        #6
    server = smtplib.SMTP("smtp.gmail.com", 587)                #7
    server.starttls()                                           #8
    server.login(os.getenv("LOGIN"), os.getenv("PASSWORD"))     #9
    server.sendmail(os.getenv("LOGIN"), email_address, message) #10
    server.quit()                                               #11
    flash("Thank you " + name + " for getting in touch, Your email has been sent",'success')
    return redirect(url_for('all_recipe'))                      #12
  return render_template('contact.html')                        #1
 
  
"""
Deatiled Recipe page
   1. Finds the id of the recipe required 
   2. Check to see if user is in session, If does this because there is a if statment in the HTML
      to check if user is the owner of the recipe, If the user is the ower, the Edit/Delete buttons are
      avaible to them"""
@app.route('/recipe/<recipe_id>')
def recipe(recipe_id):
  recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})  
  if 'username' in session:
    return render_template('recipe.html',session_name=session['username'], recipe=recipe)
  return render_template('recipe.html', recipe=recipe)
  

"""
Registering route 
  1. Checks to see if method is POST: if False-Render Template for Register 
  2. True:- Create mongo collection Variable
  3. Create time variable
  4. Check collection to see if the email already exists
  5. If False:-Flash message and redirect about to registration page
  6. Ture:- Hash password and insert into collection
  7. Create Session from form username
  8.Flash message with session name and redirect to all_recipes return out"""
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':                                              
       users = mongo.db.users                                                 
       time = datetime.datetime.now()                                         
       existing_email = users.find_one({'email': request.form['userEmail']})  
       if existing_email is None:                                             
                hashpass = bcrypt.hashpw(request.form['userPassword'].encode('utf-8'), bcrypt.gensalt())
                users.insert({                                                
                'name' : request.form['username'].capitalize(), 
                'email': request.form['userEmail'].lower(),
                'password' : hashpass,
                'reg_date' : time
                })
                session['username'] = request.form['username']   
                session['logged_in'] = True               
                flash('Hello ' + session['username'] + ' You have be successfull registered and are login In', 'success')
                return redirect(url_for('all_recipe',))                         
       flash('That email already exists, Check the spelling', 'warning')       
       return render_template('register.html')  
    return render_template('register.html')                                    



"""Login Route:
  1. Checks to see if its a post: True-Contine: False-Render Login template.
  2. Create Users var as mongo collection
  3. create login_user and find the email and request form email.
  4. check to see if login_user hashed password matches the saved hashed password.
      If False: flash message and redirect back to login page: return out
      If Ture: create session wih request form username
  5. create session login to True
  6. flash success message and redirect to all recipes """
@app.route('/login', methods=['POST','GET'])
def login():
  if request.method == 'POST': #1
      users = mongo.db.users   #2
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
  
  
  
"""Add Recipe Route:
  1. Gets todays date: convets into string(day/month/year)(subject to change in the future)
     and in iso formate
  2. If User is in session: False:-redirect to Login: Returns out. 
     True: check to see if method is POST: False:-Renders template for adding recipe: returns out
  3. Create variable for collection and Inserts from form.
  4. Flashes success message and  Redirects to all_recipe """  
@app.route('/add_recipe',methods=['POST','GET'])
def add_recipe():
  today_string = datetime.datetime.now().strftime('%d/%m/%y')
  today_iso = datetime.datetime.now()
  if 'username' in session:
      if request.method == 'POST':
          recipes = mongo.db.recipes
          recipes.insert({                          
                  'username' : request.form.get('username'),
                  'chef': request.form.get('chef'),
                  'recipe_name' : request.form.get('recipe_name'),
                  'descrition' : request.form.get('descrition'),
                  'category': request.form.get('category'),
                  'servings' : request.form.get('servings'),
                  'cooking_time' : request.form.get('cooking_time'),
                  'dish_image' : request.form.get('dish_image'),
                  'ingredients' : request.form.get('ingredients'),
                  'cooking_method' : request.form.get('cooking_method'),
                  'date_added': today_string,
                  'date_iso': today_iso})  
          
          flash('You have Successfully Added a Recipe', 'success')
          return redirect(url_for('all_recipe'))
      return  render_template("add_recipe.html", session_name=session['username'])
  flash('You Need to be Logged In to Add a New Recipe', 'warning')
  return redirect(url_for('login'))

 

"""Delete Recipe Route:
  1. If User is in session: True:-continue to get ID / False:-redirect to Login: Returns out.
  2. Get's the ID of the recipe
  3. If session name matches the user that posted the recipe:
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
    
       
    
"""Edit Recipe Route:
  1. If User is in session: True:-continue to get ID / False:-redirect to Login: return out.
  2. Get's the ID of the recipe
  3. If session name matches the user that posted the recipe: True:-Check to see if method is POST #4
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
                  'date_added': request.form.get('date_added'),
                  'update_iso' : datetime.datetime.now() })  
                 flash(' You have Successfully Updated Your Recipe', 'success')
                 return redirect(url_for('all_recipe', recipe=recipe))
              return render_template('edit_recipe.html',session_name=session['username'], recipe=recipe)#3      
    flash('Sorry! You have to Login First', 'danger')
    return redirect(url_for('login_page')) #1



"""LogOut Route 
  1. changes sessions to none
  2. makes the Loggin_in = False"""
@app.route('/logout')
def logout():
   # remove the username from the session if it's there
    session.pop('username', None)
    session['logged_in'] = False
    return redirect(url_for('all_recipe'))
  

"""Error Handerling
  If we get a 404 or 500 error the users
  is redirected to the error page. """
@app.errorhandler(404)
def page_not_found(error):
  app.logger.info(f'Page not found: {request.url}')
  return render_template('404.html', error=error)

@app.errorhandler(500)
def page_not_found(error):
  app.logger.info(f'Server Error: {request.url}')
  return render_template('500.html', error=error)
  
  
  
if __name__ == "__main__":
    app.run(host=os.environ.get('IP'),
            port=(os.environ.get('PORT')),
            debug=True)
    