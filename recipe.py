#!/usr/bin/env python3

class Recipe:
	
	def __init__(self, name, id=0, ingredients= [], notes="", cuisine=""):
		
		self.name = name
		self.ingredients = ingredients
		self.id = id
		self.notes = notes
		self.cuisine = cuisine
		
	def __str__(self):
		return self.name
		
	def instert_recipe(self, conn):
		"""
		This will insert an recipe into our database

		Args:
			conn (Connection): This is the connection to our db
		"""
		
		# First lets just add the recipe into the recipes table
		with conn:
			c = conn.cursor()
			c.execute("INSERT INTO recipes(name, notes, cuisine) VALUES (?, ?, ?)", (self.name, self.notes, self.cuisine))
			# This will retrive the last id written to the db
			file_entry = c.execute('SELECT last_insert_rowid()')
			print(f"{c.lastrowid = }")

			# Need id for each ingredient this recipe uses
			for ingredient in self.ingredients:
				print(f"{ingredient = }")
				ingredient_id = conn.execute(f"SELECT id FROM ingredients where name = '{ingredient}'").fetchone()
				
				# This gives us the id for each ingredient
				print(f"{ingredient_id['id'] = }")


				# Next we need to insert this into the menu_map table
				# c.execute("INSERT INTO menu_map(ingredient_id, recipe_id, quantity, unit)")

			
	@staticmethod
	def list_recipes(conn):
		"""
		This will return all the recipes in our database
		
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

