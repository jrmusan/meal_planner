#!/usr/bin/env python3

import json
import sys
import os
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort
import random
from datetime import timedelta

from ingredient import Ingredent
from recipe import Recipe
from user import User

from database import Database

db_obj = Database()


def random_num():
	
	random_num = random.randint(0000, 9999)

	session['user_id'] = random_num
	return None


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)

"""
================================================================================
|																			   |
|				 Below are the app routes which give route us to  pages		   |
|																			   |
================================================================================
"""


# This is just for the base home page route
@app.route('/', methods=('GET', 'POST'))
def user_page():

	# Could build a custom decorator to have this code in just one place
	if "user_id" in session:
		return redirect(url_for('selected_recipes'))

	if request.method == 'POST':

		# Check if we were given a user ID
		if request.form['submit_button'] == 'enter':
			user_id = request.form['user_id']

			# Check if this id exists
			if User.check_user(user_id):
				session['user_id'] = user_id
				session.permanent = True
				return redirect(url_for('selected_recipes'))
			else:
				flash(f"Meal Plan ID {user_id} does not exist", "error")

		# Generates a Meal plan id, writes it to the db
		elif request.form['submit_button'] == 'new':
			random_num()
			flash(f"Your Meal Plan Id is {session['user_id']} please save this somewhere")
			User.insert_user(session['user_id'])
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
	ingredient_dict = Ingredent.ingredient_combiner(recipes)

	# We render this page by passing in the posts we just returned from the db
	return render_template('selected_recipes.html', recipes=recipes, ingredients=ingredient_dict, user_id=session['user_id'])


#~~~~~~~~This is our route to see a recipe~~~~~~~~
@app.route('/<int:recipe_id>', methods=('GET', 'POST'))
def recipe(recipe_id):

	if "user_id" not in session:
		return redirect(url_for('user_page'))

	# Get this recipe object
	recipe_obj = Recipe.get_recipe(id=recipe_id)

	# Get the ingredients with units added to end
	ingredient_dict = Ingredent.ingredient_combiner([recipe_obj])

	if request.method == 'POST':
		return redirect(url_for('edit_recipe', recipe_id=recipe_id))
		
	return render_template('recipe.html', recipe=recipe_obj, ing_dict=ingredient_dict)


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

		if name.lower() in ingredients:
			flash(f'{name} already exists!', 'error')
			
		else:
			# Lets write this to the database!
			ing_obj = Ingredent(name.strip(), category=category)
			ing_obj.insert_ingredient()
			return redirect(url_for('selected_recipes'))
	
	return render_template('add_ingredient.html')
		

@app.route('/plan_meals', methods=('GET', 'POST'))
def plan_meals():

	if "user_id" not in session:
		return redirect(url_for('user_page'))
	
	# Next lets get all the recipes
	recipes = Recipe.list_recipes(session['user_id'])

	if request.method == 'POST':

		Recipe.delete_user_meals(session['user_id'])

		selected_recipes = request.values.getlist('recipes')

		# Need a way to convert a name into an id
		for recipe in selected_recipes:

			# First lets get its id
			recipe_id = Recipe.get_id_from_name(recipe)
			Recipe.add_to_meal_plan(recipe_id, session['user_id'])

		flash(f"Your Meal Plan has been updated!")
		return redirect(url_for('selected_recipes'))

	return render_template('meal_plan.html', recipes=recipes)


@app.route('/user_id', methods=('GET', 'POST'))
def get_user():

	if request.method == 'POST':

		# Check if we were given a user ID
		if request.form['submit_button'] == 'enter':
			user_id = request.form['user_id']
			print(f"{user_id = }")
			session['user_id'] = user_id

		elif request.form['submit_button'] == 'Generate new Meal Plan ID':
			# Generates a user id, writes it to the db
			random_num()
			User.insert_user(session['user_id'])

	return render_template('user.html')

@app.route('/edit_recipe/<int:recipe_id>', methods=('GET', 'POST'))
def edit_recipe(recipe_id):

	# Get this recipe object
	recipe_obj = Recipe.get_recipe(id=recipe_id)

	# Get the ingredients for auto complete 
	ingredients = Ingredent.list_ingredients()

	if request.method == 'POST':

		selected_ingredients = request.values.getlist('ingredients')
		name = request.form['name']
		notes = request.form['notes']
		cuisine = request.form['cuisine']
		
		recipe_obj.update_recipe(selected_ingredients, name, notes, cuisine)
		return redirect(url_for('selected_recipes', recipe_id=recipe_obj.id))
		
	return render_template('edit_recipe.html', ingredients=ingredients, recipe=recipe_obj)


if __name__ == "__main__":
	app.run()
