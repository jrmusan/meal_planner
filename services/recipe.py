#!/usr/bin/env python3

import re
import logging

from services.ingredient import Ingredent
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

	@property
	def selected(self):
		"""
		Checks if this recipe is selected in the meal plans

		Returns:
			True if selected for meal plan
		"""

		if Recipe.db_obj.execute(f"SELECT 1 FROM selected_meals WHERE recipe_id = '{self.id}'").fetchone():
			return True
	
		return False
	
		
	@staticmethod
	def instert_recipe(name, ingredients, user_id, notes="", cuisine="", quantity=1, unit="cup"):
		"""
		This will insert an recipe into our database

		Args:
			conn (Connection): This is the connection to our db
		"""

		# Lets do a little cleanup on the name
		letter_cleanup = re.compile("[^a-zA-Z0-9\\s]")
		name = letter_cleanup.sub('', name)

		# First lets just add the recipe into the recipes table
		Recipe.db_obj.execute("INSERT INTO recipes(name, notes, cuisine, user_id) VALUES (?, ?, ?, ?)", (name, notes, cuisine, user_id))

		# This will retrive the last id written to the db
		recipe_id = Recipe.db_obj.cursor.lastrowid

		# Need id for each ingredient this recipe uses
		insert_cmd = "INSERT INTO menu_map(ingredient_id, recipe_id, quantity, unit) VALUES (?, ?, ?, ?)"

		for ingredient in ingredients:

			# If we have ingredient objs this is a bit easier
			if isinstance(ingredient, dict):
				# Next we need to insert this into the menu_map table
				Recipe.db_obj.execute(insert_cmd, (ingredient['id'], recipe_id, ingredient['qt'], ingredient['unit']))

			else:
				Recipe.db_obj.execute(insert_cmd, (ingredient.id, recipe_id, ingredient.quantity, ingredient.unit))

		return recipe_id

	@staticmethod
	def list_recipes(user_id):
		"""
		Returns all the recipes for this user in alphabetical order
		Args:
			user_id (int): Id of the user to get selected recipes for 
		Returns:
			sqlite3.Row Obj: Ingredient rows 
		"""
		
		# Grab all the recipes from the db
		recipes = Recipe.db_obj.execute(f'SELECT * FROM recipes where user_id = {user_id}').fetchall()
		
		recipe_objs = []
		
		# Lets turn them into objs
		for recipe in recipes:
			recipe_obj = Recipe(recipe['name'], recipe['id'], recipe['notes'], recipe['cuisine'])
			recipe_objs.append(recipe_obj)

		recipe_objs.sort(key=lambda recipe: recipe.name)
				
		return recipe_objs

	@staticmethod
	def get_id_from_name(name, user_id):
		"""
		Given a recipe name, get its id

		Args:
			name (str): Name of the recipe
		
		Returns:
			int: ID of the recipe
		"""

		print(f"In Recipe.py trying to get recipe id from name: ({name})")

		id = Recipe.db_obj.execute(f"SELECT id FROM recipes where name = '{name}' AND user_id = '{user_id}'").fetchone()
		return id["id"]

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
		recipe_obj = Recipe(recipe_row['name'], id, ingredients_list, recipe_row['notes'].split('\n'), recipe_row['cuisine'])

		return recipe_obj

	@staticmethod
	def delete_user_meals(user_id):
		"""
		Removes all the selected meals for this user 

		Args:
			user_id (int): Id of the user to get selected recipes for
		"""
		
		Recipe.db_obj.execute(f"DELETE FROM selected_meals where user_id = {user_id}")

	@staticmethod
	def add_to_meal_plan(id, user_id):
		"""
		This will add this recipe to our meal plan for the week

		Args:
			id (int): Id of the recipe to add
			user_id (int): Id of the user to get selected recipes for 
		
		"""

		# Just add the recipe into the recipes table
		Recipe.db_obj.execute("INSERT INTO selected_meals(recipe_id, user_id) VALUES (?, ?)", (id, user_id))

	
	@staticmethod
	def get_selected_recipes(user_id):
		"""
		This will get all the selected meals for this meal plan

		Args:
			user_id (int): Id of the user to get selected recipes for 

		Returns:
			list []: List of Recipe objects
		"""

		# Grab all the meup_maps from from the db
		selected_recipes = Recipe.db_obj.execute(f"SELECT * FROM selected_meals where user_id = {user_id}").fetchall()

		# We need to instantiate the ingredient obj for each ingredient in this recipe
		recipe_list = []
		for recipe in selected_recipes:
			print(f"{recipe = }")
			recipe_obj = Recipe.get_recipe(recipe['recipe_id'])
			recipe_list.append(recipe_obj)

		return recipe_list

	def update_recipe(self, selected_ings, name="", notes="", cuisine="", quantity=1, unit="cup"):
		"""
		Will update the Recipe in the database if needed

		Args:
			selected_ings: List of selected ingredient objects
			name (str): Name of recipe
			notes (str): Notes for the recipe
			cuisine (str): Cuisine for the recipe
		"""

		# TODO: Find a smarter way to do this instead of just dropping everything for the Recipe		
		if len(selected_ings) >= 1 and self.ingredients != selected_ings:
			# First we are going to drop all the ingredients for this recipe
			Recipe.db_obj.execute(f"DELETE FROM menu_map where recipe_id = {self.id}")

			# Next we need to insert this into the menu_map table (HARDCODING quantity and unit for now)
			for ingredient in selected_ings:
				Recipe.db_obj.execute("INSERT INTO menu_map(ingredient_id, recipe_id, quantity, unit) VALUES (?, ?, ?, ?)", (ingredient.get("id"), self.id, ingredient.get("qt"), ingredient.get("unit")))

		# Next check if we need to update the recipe
		if self.name != name or self.notes != notes or self.cuisine != cuisine:
			Recipe.db_obj.execute('UPDATE recipes SET name = ?, notes = ?, cuisine = ?'' WHERE id = ?', (name, str(notes), cuisine, self.id))


	def delete(self):
		"""
		Given an id of a recipe, scrape it away from the DB

		"""

		# First lets drop it from selected meals just incase its currently selected
		Recipe.db_obj.execute(f"DELETE FROM selected_meals where recipe_id = {self.id}")

		# Next we are going to drop all the ingredients for this recipe
		Recipe.db_obj.execute(f"DELETE FROM menu_map where recipe_id = {self.id}")

		# Lastly, lets delete this recipe!
		Recipe.db_obj.execute(f"DELETE FROM recipes where id = {self.id}")

	@staticmethod
	def list_all_recipes(user_id):
		"""
		This will list all recipes in the databse reguardless of the user id

		Args:
			user_id (int): Id of the user find recipes that dont belong to the current user


		Returns:
			sqlite3.Row Obj: Ingredient rows
		"""
		
		# Grab all the recipes from the db
		recipes = Recipe.db_obj.execute(f'SELECT * FROM recipes where user_id != {user_id}').fetchall()
		
		recipe_objs = []
		
		# Lets turn them into objs
		for recipe in recipes:
			recipe_obj = Recipe(recipe['name'], recipe['id'], recipe['notes'], recipe['cuisine'])
			recipe_objs.append(recipe_obj)
				
		return recipe_objs

	@staticmethod
	def copy_recipe(recipe_obj, user_id):
		"""
		Given a recipe ID copy all its data over to the other user

		Args:
			recipe_obj: (Recipe): ID of recipe to copy over to other user
			user_id (int): Id of the user to copy the recipe to
		"""

		# To make this simple lets just call insert recipe with the current users id
		new_id = Recipe.instert_recipe(recipe_obj.name, recipe_obj.ingredients, user_id, '\n'.join(recipe_obj.notes), recipe_obj.cuisine)
