#!/usr/bin/env python3

class Recipe:
	
	def __init__(self, name, id=0, notes="", cuisine=""):
		
		self.name = name
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
		
		with conn:
			c = conn.cursor()
			c.execute("INSERT INTO recipes(name, notes, cuisine) VALUES (?, ?, ?)", (self.name, self.notes, self.cuisine))
			
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