#!/usr/bin/env python3

from ingredient import Ingredent

class Recipe:
	
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
	def list_recipes(conn):
		"""
		This will return all the recipes in our database (THIS SHOULD JUST CALL GET_RECIPE)
		
		Args:
			conn (Connection): This is the connection to our db
		Returns:
			sqlite3.Row Obj: Ingredient rows 
		"""
		
		with conn:
			c = conn.cursor()
			
			# Grab all the recipes from the db
			recipes = conn.execute('SELECT * FROM recipes').fetchall()
			
			recipe_objs = []
			
			# Lets turn them into objs
			for recipe in recipes:
				recipe_obj = Recipe(recipe['name'], recipe['id'], recipe['notes'], recipe['cuisine'])
				recipe_objs.append(recipe_obj)
				
			return recipe_objs

	@staticmethod
	def get_recipe(conn, id):
		"""
		This will get the recipe along with its ingredient objects

		Args:
			conn (Connection): This is the connection to our db
		"""

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