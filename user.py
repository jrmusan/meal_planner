from os import stat
from ingredient import Ingredent
from database import Database

class User:

    db_obj = Database()
	
    def __init__(self, user_id):

        self.user_id = user_id

    
    def insert_user(user_id):
        """
        Inserts a user into the user_id database

        Args:
			user_id (int): Id of the user to get selected recipes for 
        """

        # First lets just add the recipe into the recipes table
        print(f"Trying to insert: {user_id}")

        User.db_obj.execute("INSERT INTO user_table(user_id) VALUES (?)", (user_id,))