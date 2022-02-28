#!/usr/bin/env python3

class Ingredent:
	
	def __init__(self, name, category = "", quantity = 0, unit = ""):
	
		self.name = name
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
			c = conn.cursor()
			ingredients = conn.execute('SELECT * FROM ingredients').fetchall()
			for ing in ingredients:
				print(f"Ingredient name: {ing['name']}")
			
			return ingredients
		
		