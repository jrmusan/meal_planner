#!/usr/bin/env python3

class Recipe:
	
	def __init__(self, name, notes="", cuisine=""):
		
		self.name = name
		self.notes = notes
		self.cuisine = cuisine
		
	def instert_recipe(self, conn):
		"""
		This will insert an recipe into our database

		Args:
			conn (Connection): This is the connection to our db
		"""
		
		with conn:
			c = conn.cursor()
			c.execute("INSERT INTO recipes(name, notes, cuisine) VALUES (?, ?, ?)", (self.name, self.notes, self.cuisine))