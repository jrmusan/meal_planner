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
	def instert_recipe(name, ingredients, notes="", cuisine="", quantity=1, unit="cup"):
		"""
		This will insert an recipe into our database

		Args:
			conn (Connection): This is the connection to our db
		"""
		
		# First lets just add the recipe into the recipes table
		Recipe.db_obj.execute("INSERT INTO recipes(name, notes, cuisine) VALUES (?, ?, ?)", (name, notes, cuisine))

		# This will retrive the last id written to the db
		recipe_id = Recipe.db_obj.cursor.lastrowid

		# Need id for each ingredient this recipe uses
		for ingredient in ingredients:

			print(f"{ingredient = }")

			ingredient_id = Recipe.db_obj.execute(f"SELECT id FROM ingredients where name = '{ingredient}'").fetchone()

			print(f"{ingredient_id['id'] = }")
			
			# Next we need to insert this into the menu_map table (HARDCODING quantity and unit for now)
			Recipe.db_obj.execute("INSERT INTO menu_map(ingredient_id, recipe_id, quantity, unit) VALUES (?, ?, ?, ?)", (ingredient_id['id'], recipe_id, quantity, unit))

		return recipe_id

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

	@staticmethod
	def get_id_from_name(name):
		"""
		Given a recipe name, get its id

		Args:
			name (str): Name of the recipe
		
		Returns:
			int: ID of the recipe
		
		"""

		id = Recipe.db_obj.execute(f"SELECT id FROM recipes where name = '{name}'").fetchone()
		return id["id"]

	@staticmethod # ~~~~~~~~~~~~CONSIDER THIS METHOD USING EITHER A NAME OR ID~~~~~~~~~~~~
	def get_recipe(id):
		"""
		This will get the recipe along with its ingredient objects

		Args:
			conn (Connection): This is the connection to our db
		"""

		# Grab all the meup_maps from from the db
		ingredients = Recipe.db_obj.execute(f"SELECT * FROM menu_map where recipe_id = '{id}'").fetchall()

		# We need to instantiate the ingredient obj for each ingredient in this recipe
		ingredients_list = []
		for ing in ingredients:
			ing_obj = Ingredent.get_ingredient(ing['ingredient_id'], ing['quantity'], ing['unit'])
			ingredients_list.append(ing_obj)

		# Query recipe database to get recipe table from ID
		recipe_row = Recipe.db_obj.execute(f"SELECT name, notes, cuisine FROM recipes where id = {id}").fetchone()

		# Next instantiate the recipe object
		recipe_obj = Recipe(recipe_row['name'], id, ingredients_list, recipe_row['notes'], recipe_row['cuisine'])

		return recipe_obj

	@staticmethod
	def add_to_meal_plan(id):
		"""
		This will add this recipe to our meal plan for the week

		Args:
			conn (Connection): This is the connection to our db
		
		"""

		# First lets just add the recipe into the recipes table
		print(f"Trying to insert: {id}")
		Recipe.db_obj.execute("INSERT INTO selected_meals(recipe_id) VALUES (?)", (id,))


	@staticmethod
	def get_selected_recipes():
		"""
		This will get all the selected meals for this meal plan

		Args:
			conn (Connection): This is the connection to our db
		Returns:
			sqlite3.Row Obj: Ingredient rows 
		
		"""

		# Grab all the meup_maps from from the db
		selected_recipes = Recipe.db_obj.execute(f"SELECT * FROM selected_meals").fetchall()

		print(f"{selected_recipes = }")

		# We need to instantiate the ingredient obj for each ingredient in this recipe
		recipe_list = []
		for recipe in selected_recipes:
			print(f"{recipe = }")
			recipe_obj = Recipe.get_recipe(recipe['recipe_id'])
			recipe_list.append(recipe_obj)

		return recipe_list
