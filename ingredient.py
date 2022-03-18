#!/usr/bin/env python3

from database import Database

class Ingredent:

	db_obj = Database()
	
	def __init__(self, name, id = 0, category = "", quantity = 0, unit = ""):
	
		self.name = name
		self.id = id
		self.category = category
		self.quantity = quantity
		self.unit = unit
		
	def __str__(self):
		return self.name
		
	def insert_ingredient(self):
		"""
		This will insert an ingredient into our database

		Args:
			conn (Connection): This is the connection to our db
		"""

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
			ingredient_obj = Ingredent(ing['name'], ing['id'], ing['category'])
			
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