#!/usr/bin/env python3

class Ingredent:
	
	def __init__(self, name, id = 0, category = "", quantity = 0, unit = ""):
	
		self.name = name
		self.id = id
		self.category = category
		self.quantity = quantity
		self.unit = unit
		
	def __str__(self):
		return self.name
		
	def insert_ingredient(self, conn):
		"""
		This will insert an ingredient into our database

		Args:
			conn (Connection): This is the connection to our db
		"""

		with conn:
			c = conn.cursor()
			c.execute("INSERT INTO ingredients(name, category) VALUES (?, ?)", (self.name, self.category))
			
	@staticmethod
	def list_ingredients(conn):
		"""
		This will return all the ingredients in our database
		
		Args:
			conn (Connection): This is the connection to our db
		Returns:
			sqlite3.Row Obj: Ingredient rows 
		"""
		
		with conn:
			ingredients = conn.execute('SELECT * FROM ingredients').fetchall()
			
			# Lets turn these into objects
			ingredient_objs = []
			
			for ing in ingredients:
				ingredient_obj = Ingredent(ing['name'], ing['id'], ing['category'])
				
				ingredient_objs.append(ingredient_obj)
				
			return ingredient_objs

	@staticmethod
	def get_ingredient(conn, id, quantity, unit):
		"""
		Retruns an ingredient obj
		"""
		
		# Get the data for this ingredient
		ingredient_row = conn.execute(f"SELECT name, category FROM ingredients where id = '{id}'").fetchone()

		# Instantiate an Ingredent object with eveyrthing it needs
		ing_obj = Ingredent(ingredient_row['name'], id, ingredient_row['category'], quantity, unit)
		return ing_obj