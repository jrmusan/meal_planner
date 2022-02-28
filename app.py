#!/usr/bin/env python3

import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

from ingredient import Ingredent
from recipe import Recipe

# This will return a database connection to our SQLite db
# This will return rows from the db that are just dicts
def get_db_connection():
	conn = sqlite3.connect('database.db')
	conn.row_factory = sqlite3.Row
	return conn

def get_recipe(recipe_id):
	conn = get_db_connection()
	
	# This is running a sql command to get a posts by it's id
	recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,)).fetchone()
	conn.close()
	if recipe is None:
		abort(404)
	return recipe

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkeyohwowcrazy'

"""
================================================================================
|																			   |
|				 Below are the app routes which give route us to  pages		   |
|																			   |
================================================================================
"""


# This is just for the base home page route
@app.route('/')
def index():
	
	# This will open the db connection
	conn = get_db_connection()
	
	# Next we select all entries in the (posts) table
#	recipes = conn.execute('SELECT * FROM recipes').fetchall()
	recipes = Recipe.list_recipes(conn)
	
	# We render this page by passing in the posts we just returned from the db
	return render_template('index.html', recipes=recipes)


#~~~~~~~~This is our route to see a recipe~~~~~~~~
@app.route('/<int:recipe_id>')
def recipe(recipe_id):
	recipe = get_recipe(recipe_id)
	return render_template('recipe.html', recipe=recipe)


#~~~~~~~~This is our route to create a new recipe~~~~~~~~
@app.route('/create', methods=('GET', 'POST'))
def create():
	
	# Get the ingredients for auto complete
	conn = get_db_connection()
	ingredients = Ingredent.list_ingredients(conn)
		
	# Checks if a post was sent
	if request.method == 'POST':
		# If so grab the input data from the page submitted
		name = request.form['name']
		notes = request.form['notes']
		cuisine = request.form['cuisine']
		
		if not name:
			flash('Name is required!')
		else:
			# Lets write this to the database!
			recipe_obj = Recipe(name, notes, cuisine)
			recipe_obj.instert_recipe(conn)
			return redirect(url_for('index'))
		
	return render_template('create.html', ingredients=ingredients)


#~~~~~~~~This is our route to add a new ingredient~~~~~~~~
@app.route('/create_ingredient', methods=('GET', 'POST'))
def add_ingredient():
	
	# Checks if a post was sent
	if request.method == 'POST':
		# If so grab the input data from the page submitted
		name = request.form['name']
		category = request.form['category']
	
		if not name:
			flash('Name is required!')
			
		else:
			# Lets write this to the database!
			conn = get_db_connection()
			ing_obj = Ingredent(name, category)
			ing_obj.insert_ingredient(conn)
			return redirect(url_for('index'))
	
	return render_template('add_ingredient.html')
		
	


#~~~~~~~~This will edit a recipe~~~~~~~~
@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
	
	# This will get the ID that was selected
	post = get_post(id)
	
	if request.method == 'POST':
		title = request.form['title']
		content = request.form['content']
		
		if not title:
			flash('Title is required!')
		else:
			conn = get_db_connection()
			conn.execute('UPDATE posts SET title = ?, content = ?'' WHERE id = ?', (title, content, id))
			conn.commit()
			conn.close()
			return redirect(url_for('index'))
		
	return render_template('edit.html', post=post)