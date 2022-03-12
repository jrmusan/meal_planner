#!/usr/bin/env python3

from os import stat
from ingredient import Ingredent
from database import Database

class Recipe:

	db_obj = Database()
	
	def __init__(self, name, id=0, ingredients=[], notes="", cuisine=""):
		
		self.name = name
		self.ingredients = ingredients
		self.id = id
		self.notes = notes
		self.cuisine = cuisine
		
	def __str__(self):
		return self.name
		
	@staticmethod
	def instert_recipe(conn, name, ingredients, notes="", cuisine="", quantity=1, unit="cup"):
		"""
		This will insert an recipe into our database

		Args:
			conn (Connection): This is the connection to our db
		"""
		
		# First lets just add the recipe into the recipes table
		with conn:
			c = conn.cursor()
			c.execute("INSERT INTO recipes(name, notes, cuisine) VALUES (?, ?, ?)", (name, notes, cuisine))
			# This will retrive the last id written to the db
			recipe_id = c.lastrowid

			# Need id for each ingredient this recipe uses
			for ingredient in ingredients:
				ingredient_id = conn.execute(f"SELECT id FROM ingredients where name = '{ingredient}'").fetchone()
				
				# Next we need to insert this into the menu_map table (HARDCODING quantity and unit for now)
				c.execute("INSERT INTO menu_map(ingredient_id, recipe_id, quantity, unit) VALUES (?, ?, ?, ?)", (ingredient_id['id'], recipe_id, quantity, unit))

	@staticmethod
	def list_recipes():
		"""
		This will return all the recipes in our database (THIS SHOULD JUST CALL GET_RECIPE)
		
		Args:
			conn (Connection): This is the connection to our db
		Returns:
			sqlite3.Row Obj: Ingredient rows 
		"""
		
			
		# Grab all the recipes from the db
		recipes = Recipe.db_obj.execute('SELECT * FROM recipes').fetchall()
		
		recipe_objs = []
		
		# Lets turn them into objs
		for recipe in recipes:
			recipe_obj = Recipe(recipe['name'], recipe['id'], recipe['notes'], recipe['cuisine'])
			recipe_objs.append(recipe_obj)
				
			return recipe_objs

	@staticmethod # ~~~~~~~~~~~~CONSIDER THIS METHOD USING EITHER A NAME OR ID~~~~~~~~~~~~
	def get_recipe(conn, id=0, name=""):
		"""
		This will get the recipe along with its ingredient objects

		Args:
			conn (Connection): This is the connection to our db
		"""

		# If were given a name, make a single call to get the id for this recipe
		if not id and name:
			id = conn.execute(f"SELECT id FROM recipes where name = '{name}'").fetchall()
			print(f"{id = }")


		# Grab all the meup_maps from from the db
		ingredients = conn.execute(f"SELECT * FROM menu_map where recipe_id = '{id}'").fetchall()

		# We need to instantiate the ingredient obj for each ingredient in this recipe
		ingredients_list = []
		for ing in ingredients:
			ing_obj = Ingredent.get_ingredient(conn, ing['ingredient_id'], ing['quantity'], ing['unit'])
			ingredients_list.append(ing_obj)

		# Query recipe database to get recipe table from ID
		recipe_row = conn.execute(f"SELECT name, notes, cuisine FROM recipes where id = {id}").fetchone()

		# Next instantiate the recipe object
		recipe_obj = Recipe(recipe_row['name'], id, ingredients_list, recipe_row['notes'], recipe_row['cuisine'])

		return recipe_obj

	@staticmethod
	def add_to_meal_plan(conn, id):
		"""
		This will add this recipe to our meal plan for the week

		Args:
			conn (Connection): This is the connection to our db
		
		"""

		# First lets just add the recipe into the recipes table
		with conn:
			c = conn.cursor()
			print(f"Trying to insert: {id}")
			c.execute("INSERT INTO selected_meals(id) VALUES (?)", (id))


	@staticmethod
	def get_selected_recipes(conn):
		"""
		This will get all the selected meals for this meal plan

		Args:
			conn (Connection): This is the connection to our db
		Returns:
			sqlite3.Row Obj: Ingredient rows 
		
		"""

		# Grab all the meup_maps from from the db
		selected_recipes = conn.execute(f"SELECT * FROM selected_meals").fetchall()

		# We need to instantiate the ingredient obj for each ingredient in this recipe
		recipe_list = []
		for recipe in selected_recipes:
			recipe_obj = Recipe.get_recipe(conn, recipe['recipe_id'])
			recipe_list.append(recipe_obj)

		return recipe_list
