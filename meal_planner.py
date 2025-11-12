#!/usr/bin/env python3

import json
import os
from flask import Flask, jsonify, render_template, request, url_for, flash, redirect, session, redirect, url_for
from datetime import timedelta
from better_profanity import profanity
import logging

from services.ingredient import Ingredent
from services.recipe import Recipe
from services.user import User
from dotenv import load_dotenv

# OAuth setup using google-auth-oauthlib (server-side flow)
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from flask import session

from database import Database

db_obj = Database()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)

# Load environment variables from .env file
load_dotenv()

# configure logging for easier oauth debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
if os.environ.get('DEBUG'):
	logger.setLevel(logging.DEBUG)



# helper to build client config from env vars (works without a client_secrets.json)
def _build_google_client_config():
	return {
		"web": {
			"client_id": os.getenv('GOOGLE_CLIENT_ID'),
			"client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
			"auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
			"token_uri": "https://oauth2.googleapis.com/token",
		}
	}

# Use the full OAuth scope URLs — google will expand short names like 'email' to these
SCOPES = [
	'openid',
	'https://www.googleapis.com/auth/userinfo.email',
	'https://www.googleapis.com/auth/userinfo.profile',
]


# This is a basic about me apge
@app.route('/about')
def about():
	return render_template('about_me.html')

# This is just for the base home page route
@app.route('/', methods=('GET', 'POST'))
def user_page():

	# Could build a custom decorator to have this code in just one place
	if "user_id" in session:
		return redirect(url_for('selected_recipes'))

	if request.method == 'POST':

		# Try to get the userID
		user_id = request.form.get('user_id')
		if not user_id:
			flash("You need to enter a Meal Plan Id - If you don't have one, enter a number you will remember")
			return render_template('user.html')

		# Check if we were given a user ID
		if request.form.get('submit_button') == 'enter':
			# Check if this id exists
			if User.get_backend_id(user_id):
				session['user_id'] = user_id
				session.permanent = True
				return redirect(url_for('selected_recipes'))
			else:
				flash(f"Meal Plan ID {user_id} does not exist", "error")

		# Lets user pick a new Meal plan id, writes it to the db
		elif request.form.get('submit_button') == 'new':

			# Check if this user id is already being used
			if User.get_backend_id(user_id):
				flash(f"Meal Plan ID {user_id} already exists. Be more creative", "error")
			else:
				flash(f"Your Meal Plan Id is {user_id} please save this somewhere")
				User.insert_user(user_id)
				session['user_id'] = user_id
				session.permanent = True
				return redirect(url_for('selected_recipes'))

	return render_template('user.html')


@app.route('/login')
def login():
	# Basic sanity check so we don't forward a malformed request to Google
	client_id = os.getenv('GOOGLE_CLIENT_ID')
	if not client_id:
		flash('Google OAuth is not configured: GOOGLE_CLIENT_ID is missing in the environment.', 'error')
		return redirect(url_for('user_page'))

	redirect_uri = url_for('authorize', _external=True)
	logger.info('Starting Google OAuth login. client_id present=%s, redirect_uri=%s', bool(client_id), redirect_uri)
	try:
		client_config = _build_google_client_config()
		if not client_config['web']['client_id']:
			flash('Google OAuth CLIENT_ID not configured', 'error')
			return redirect(url_for('user_page'))

		flow = Flow.from_client_config(
			client_config,
			scopes=SCOPES,
			redirect_uri=redirect_uri,
		)

		authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true', prompt='consent')
		session['oauth_state'] = state
		logger.info('Google authorize URL: %s', authorization_url)
		return redirect(authorization_url)
	except Exception as err:
		logger.exception('Failed to start google oauth flow')
		flash(f'Failed to start Google OAuth: {str(err)}', 'error')
		return redirect(url_for('user_page'))


@app.route('/authorize')
def authorize():
	try:

		logger.info('Google authorize callback received')

		state = session.pop('oauth_state', None)
		if not state:
			flash('Missing OAuth state in session; try logging in again.', 'error')
			return redirect(url_for('user_page'))

		client_config = _build_google_client_config()
		flow = Flow.from_client_config(
			client_config,
			scopes=SCOPES,
			state=state,
			redirect_uri=url_for('authorize', _external=True),
		)
		# exchange the authorization code for credentials
		flow.fetch_token(authorization_response=request.url)
		creds = flow.credentials

		# verify the ID token and extract user info
		idinfo = id_token.verify_oauth2_token(creds.id_token, grequests.Request(), client_config['web']['client_id'])
		google_sub = idinfo.get('sub')
		email = idinfo.get('email')
		name = idinfo.get('name')
		logger.info('Google userinfo received: sub=%s, email=%s', google_sub, email)
	except Exception as err:
		logger.exception('Google authorize callback processing failed')
		flash(f'Error completing Google sign-in: {str(err)}', 'error')
		return redirect(url_for('user_page'))

	# Try find a local user by google_sub
	local_user = User.get_by_google_sub(google_sub)
	if not local_user:
		# Try find by email and associate
		local_user = User.get_by_email(email)
		if local_user:
			User.set_google_for_user(local_user, google_sub, email, name)
		else:
			# create a new local user and map
			new_user_id = User.create_with_google(google_sub, email, name)
			local_user = new_user_id

	# Set our session just like the existing flow
	session['user_id'] = local_user
	session.permanent = True
	return redirect(url_for('selected_recipes'))


@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('user_page'))
	

@app.route('/selected_recipes')
def selected_recipes():

	if "user_id" not in session:
		return redirect(url_for('user_page'))

	# Next lets get all the recipes
	recipes = Recipe.get_selected_recipes(session['user_id'])

	# Need to pass in a full list of ingredients we need for all these recipes
	ingredient_list = Ingredent.ingredient_combiner(recipes)

	users_in_cart_items = User.get_in_cart_items(session['user_id'])

	# We render this page by passing in the posts we just returned from the db
	return render_template('selected_recipes.html', recipes=recipes, ingredients=ingredient_list, user_id=session['user_id'], users_in_cart_items=users_in_cart_items, ingredient_ids=users_in_cart_items)


@app.route('/usage')
def usage():
	"""
	Renders the usage page for the user.

	The usage page displays the top 10 most frequently used recipes for the user.

	Returns:
		render_template('usage.html', data=data)

	Where data is a list of dictionaries containing the id, name and times_used of the recipes.
	"""

	if "user_id" not in session:
		return redirect(url_for('user_page'))

	# Get top used recipes for this user
	rows = db_obj.execute(f"SELECT id, name, times_used FROM recipes WHERE user_id = {session['user_id']} ORDER BY times_used DESC LIMIT 10").fetchall()

	data = [{ 'id': r['id'], 'name': r['name'], 'times_used': r['times_used'] } for r in rows]

	return render_template('usage.html', data=data)


#~~~~~~~~This is our route to see a recipe~~~~~~~~
@app.route('/<int:recipe_id>', methods=('GET', 'POST'))
def recipe(recipe_id):

	if "user_id" not in session:
		return redirect(url_for('user_page'))

	# Get this recipe object
	recipe_obj = Recipe.get_recipe(id=recipe_id)

	ingredient_list = Ingredent.ingredient_combiner([recipe_obj])

	if request.method == 'POST':
		if request.form['submit_button'] == 'delete':
			# Delete this recipe, redirect to home
			recipe_obj.delete()
			flash(f"Deleted {recipe_obj.name}, ewww!!!")
			return redirect(url_for('user_page'))
		else:
			return redirect(url_for('edit_recipe', recipe_id=recipe_id))
		
	return render_template('recipe.html', recipe=recipe_obj, ingredients=ingredient_list)


#~~~~~~~~This is our route to create a new recipe~~~~~~~~
@app.route('/create', methods=('GET', 'POST')) 
def create():

	if "user_id" not in session:
		return redirect(url_for('user_page'))
	
	# Get the ingredients for auto complete
	ingredients = Ingredent.list_ingredients()

	ingredient_list = [{"id": ing.id, "quantity": ing.quantity, "unit": ing.unit} for ing in ingredients]

		
	# Checks if a post was sent
	if request.method == 'POST':
		# If so grab the input data from the page submitted
		post_data = request.get_json(force=True)
		if post_data is None:
			return jsonify({'error': 'invalid json payload'}), 400

		name = post_data.get('name')
		notes = post_data.get('notes')
		cuisine = post_data.get('cuisine')
		selected_ingredients = post_data.get('selected_ingredients')
		
		if not name:
			return jsonify({'error': 'A name is required'}), 400
		elif profanity.contains_profanity(name):
			return jsonify({'error': 'Profanity is not allowed...'}), 400
		else:
			recipe_id = Recipe.instert_recipe(name.strip(), selected_ingredients, session['user_id'], notes, cuisine)
			redirect_url = url_for('recipe', recipe_id=recipe_id)

			# This will return data back to the jquery method, which will then redirect. 
			return json.dumps({'success' : True, 'url': redirect_url}), 200, {'ContentType' : 'application/json'}
		
	return render_template('create.html', ingredients=ingredients, ing_dict=ingredient_list)

#~~~~~~~~This is our route to add a new ingredient~~~~~~~~
@app.route('/add_ingredient', methods=('GET', 'POST'))
def add_ingredient():

	if "user_id" not in session:
		return redirect(url_for('user_page'))

	ingredients = Ingredent.list_ingredients()
	
	# Checks if a post was sent
	if request.method == 'POST':
		# If so grab the input data from the page submitted
		name = request.form['name']
		category = request.form['category']

		if not name:
			flash('Name is required!', 'error')

		elif profanity.contains_profanity(name):
			flash('Profanity is not allowed!', 'error')
		
		elif not category:
			flash('Category is required!', 'error')

		elif name.lower() in ingredients:
			flash(f'{name} already exists!', 'error')
			
		else:
			# Lets write this to the database!
			ing_obj = Ingredent(name.strip(), category=category)
			ing_obj.insert_ingredient()
			flash(f'Added: {name.strip()}')
			return redirect(url_for('add_ingredient'))
	
	return render_template('add_ingredient.html', ingredients=ingredients)
		

@app.route('/plan_meals', methods=('GET', 'POST'))
def plan_meals():

	if "user_id" not in session:
		return redirect(url_for('user_page'))
	
	# Next lets get all the recipes
	recipes = Recipe.list_recipes(session['user_id'])

	if request.method == 'POST':

		if request.form['submit_button'] == 'remove_button':
			print("~~~~Removing all selected recipes~~~~")
			# Lets delete all the selected meals for this user
			User.remove_selected_recipes(session['user_id'])
			return redirect(url_for('plan_meals'))

		else:
			Recipe.delete_user_meals(session['user_id'])
			User.delete_user_cart(session['user_id'])

			selected_recipes = request.values.getlist('recipes')

			# Need a way to convert a name into an id
			for recipe in selected_recipes:

				# First lets get its id
				recipe_id = Recipe.get_id_from_name(recipe, session['user_id'])
				Recipe.add_to_meal_plan(recipe_id, session['user_id'])
				# Increment the times_used counter for this recipe
				Recipe.increment_times_used(recipe_id, session['user_id'])

		flash(f"Your Meal Plan has been updated!")
		return redirect(url_for('selected_recipes'))

	return render_template('meal_plan.html', recipes=recipes)


@app.route('/edit_recipe/<int:recipe_id>', methods=('GET', 'POST'))
def edit_recipe(recipe_id):

	#~~~~~~~THIS WILL NEED THE SAME REFACTORING THAT CREATE NEEDED TO GET MODAL DATA~~~~~~~

	# Get this recipe object
	recipe_obj = Recipe.get_recipe(id=recipe_id)

	# Get the ingredients for auto complete 
	ingredients = Ingredent.list_ingredients()

	ingredient_obj_list = Ingredent.ingredient_combiner([recipe_obj])
	ingredient_list = [{"id": ing.id, "quantity": ing.quantity, "unit": ing.unit} for ing in ingredient_obj_list]

	if request.method == 'POST':

		post_data = request.get_json(force=True)
		if post_data is None:
			return jsonify({'error': 'invalid json payload'}), 400
		name = post_data.get('name')
		notes = post_data.get('notes')
		cuisine = post_data.get('cuisine')
		selected_ingredients = post_data.get('selected_ingredients')
		
		recipe_obj.update_recipe(selected_ingredients, name, notes, cuisine)

		# This will return data back to the jquery method, which will then redirect. 
		redirect_url = url_for('recipe', recipe_id=recipe_obj.id)
		return json.dumps({'success' : True, 'url': redirect_url}), 200, {'ContentType' : 'application/json'}
		
		
	return render_template('edit_recipe.html', ingredients=ingredients, recipe=recipe_obj, ing_dict=ingredient_list)

@app.route('/copy_recipes/', methods=('GET', 'POST'))
def copy_recipes():

	# Lets get all the recipes
	recipes = Recipe.list_all_recipes(session['user_id'])

	return render_template('copy_recipe.html', recipes=recipes)

@app.route('/copy_recipe/<int:recipe_id>', methods=('GET', 'POST'))
def copy_recipe(recipe_id):

	# Get this recipe object
	recipe_obj = Recipe.get_recipe(id=recipe_id)

	ingredient_list = Ingredent.ingredient_combiner([recipe_obj])

	if request.method == 'POST':
		if request.form.get('submit_button') == 'copy':
			Recipe.copy_recipe(recipe_obj, session['user_id'])
			flash(f"Copied {recipe_obj.name}, YUM!!!")
	return render_template('recipe_no_edit.html', recipe=recipe_obj, ingredients=ingredient_list)

@app.route('/update-ingredient/<int:ingredient_id>', methods=['POST'])
def update_ingredient(ingredient_id):

	print(f"Updating ingredient to be set as used {ingredient_id}")
	Ingredent.set_ingredient_as_selected(ingredient_id, session['user_id'])

	return redirect(url_for('selected_recipes'))


if __name__ == "__main__":
	app.run()
