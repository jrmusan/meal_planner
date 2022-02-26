#!/usr/bin/env python3

class Ingredent:
	
	def __init__(self, name, category = "", quantity = 0, unit = ""):
	
		self.name = name
		self.category = category
		self.quantity = quantity
		self.unit = unit
		
	def insert_ingredient(self, conn):
		"""
		This will insert an ingredient into our database

		Args:
			conn (Connection): This is the connection to our db
		"""
		
		with conn:
			c.execute("INSERT INTO ingredients VALUES(:name, :category)", {'name': self.name, 'category': self.category})
		
		