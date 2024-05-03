#!/usr/bin/env python3

import re
import json
from database import Database

class Ingredent:

	db_obj = Database()
	
	def __init__(self, name, id = 0, category = "", quantity = 1, unit = ""):
	
		self.name = name
		self.id = id
		self.category = category
		self.quantity = quantity
		self.unit = unit
		
	def __repr__(self):
		return self.name

	@property
	def json(self):
		return {"id": self.id, "name": self.name}

	def toJson(self):
		return json.dumps(self, default=lambda o: o.__dict__)

	# This is used to compare ingredients to others
	def __eq__(self, other):
		return self.name.lower() == other
		
	def insert_ingredient(self):
		"""
		This will insert an ingredient into our database

		Args:
			conn (Connection): This is the connection to our db
		"""

		# Lets do a little cleanup on the name
		letter_cleanup = re.compile("[^a-zA-Z0-9\\s]")
		self.name = letter_cleanup.sub('', self.name)

		Ingredent.db_obj.execute("INSERT INTO ingredients(name, category) VALUES (?, ?)", (self.name, self.category))
			
	@staticmethod
	def list_ingredients():
		"""
		This will return all the ingredients in our database
		
		Args:
			conn (Connection): This is the connection to our db
		Returns:
			sqlite3.Row Obj: Ingredient rows 
		"""
		
		ingredients = Ingredent.db_obj.execute('SELECT * FROM ingredients').fetchall()
		
		# Lets turn these into objects
		ingredient_objs = []
		
		for ing in ingredients:
			ingredient_obj = Ingredent(ing['name'].capitalize(), ing['id'], ing['category'])
			
			ingredient_objs.append(ingredient_obj)
			
		return ingredient_objs

	@staticmethod
	def get_ingredient(id, quantity, unit):
		"""
		Retruns an ingredient obj
		"""
		
		# Get the data for this ingredient
		ingredient_row = Ingredent.db_obj.execute(f"SELECT name, category FROM ingredients where id = '{id}'").fetchone()

		# Instantiate an Ingredent object with eveyrthing it needs
		ing_obj = Ingredent(ingredient_row['name'], id, ingredient_row['category'], quantity, unit)
		return ing_obj

	@staticmethod
	def ingredient_combiner(recipes):
		"""
		Given a list of Recipe Objects, return a list of all the required ingredient objects

		Args:
			Recipe[]:  List of recipe objects

		Returns:
			Ingredient{}: Dict with ingredient names and their quantities
		
		"""

		ingredient_objs = []

		# Need to get a total count of each ingredient for each recipe
		for recipe in recipes:
			for ingredient in recipe.ingredients:
				
				# Check if this ingredient is already in the list
				if any(ing.name == ingredient.name for ing in ingredient_objs):
					existing_ingredient = next(ing for ing in ingredient_objs if ing.name == ingredient.name)
					existing_ingredient.quantity += ingredient.quantity
				else:
					ingredient_objs.append(ingredient)

		return ingredient_objs

	def delete(self):
		"""
		This is to only be ran locally now to clean up the database
		Basically check to see if any recipe is using the given ingredient

		STRECH GOAL: Return simular ingredients with simular names

		STRECH GOAL: Write function to get all ingredients NOT used by any recipes
		"""

		# First check if any recipe is using this ingredient
		recipeIds = Ingredent.db_obj.execute(f'SELECT recipe_id FROM menu_map where ingredient_id = {self.id}').fetchall()

		if len(recipeIds) >= 1:

			print(f"{self.name} is NOT safe to delete, its being used by:")
			for sqlRow in recipeIds:
				recipeId = sqlRow["recipe_id"]
				recipe_name = Ingredent.db_obj.execute(f'SELECT name FROM recipes where id = {recipeId}').fetchone()
				print(recipe_name["name"])

		else:
			print(f"{self.name} is safe to delete... Deleting")
			recipe_name = Ingredent.db_obj.execute(f"DELETE FROM ingredients where id = {self.id}")

	@staticmethod
	def	set_ingredient_as_selected(ingredient_id, user_id):
		"""
		This will set the ingredient as selected for the user

		Args:
			ingredient_id (int): Id of the ingredient to set as selected
			user_id (int): Id of the user to set the ingredient as selected for
		"""

		Ingredent.db_obj.execute("INSERT INTO user_cart_mapping(user_id, ingredient_id) VALUES (?, ?)", (user_id, ingredient_id))

