#!/usr/bin/env python3

import json
import os
from flask import Flask, render_template, request, url_for, flash, redirect, session, redirect, url_for
from datetime import timedelta

from ingredient import Ingredent
from recipe import Recipe
from user import User

from database import Database

db_obj = Database()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)


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
		if request.form['submit_button'] == 'enter':
			user_id = request.form['user_id']

			# Check if this id exists
			if User.get_backend_id(user_id):
				session['user_id'] = user_id
				session.permanent = True
				return redirect(url_for('selected_recipes'))
			else:
				flash(f"Meal Plan ID {user_id} does not exist", "error")

		# Lets user pick a new Meal plan id, writes it to the db
		elif request.form['submit_button'] == 'new':

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
		
	# Checks if a post was sent
	if request.method == 'POST':
		# If so grab the input data from the page submitted
		post_data = request.get_json(force=True)

		name = post_data['name']
		notes = post_data['notes']
		cuisine = post_data['cuisine']
		selected_ingredients = post_data['selected_ingredients']
		
		if not name:
			flash('Name is required!', 'error')
		else:
			recipe_id = Recipe.instert_recipe(name.strip(), selected_ingredients, session['user_id'], notes, cuisine)
			redirect_url = url_for('recipe', recipe_id=recipe_id)

			# This will return data back to the jquery method, which will then redirect. 
			return json.dumps({'success' : True, 'url': redirect_url}), 200, {'ContentType' : 'application/json'}
		
	return render_template('create.html', ingredients=ingredients)


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
		name = post_data['name']
		notes = post_data['notes']
		cuisine = post_data['cuisine']
		selected_ingredients = post_data['selected_ingredients']
		
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
		if request.form['submit_button'] == 'copy':
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
