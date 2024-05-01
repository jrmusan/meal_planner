from database import Database

class User:

    db_obj = Database()
	
    def __init__(self, user_id):

        self.user_id = user_id

    @staticmethod
    def insert_user(user_id):
        """
        Inserts a user into the user_id database

        Args:
			user_id (int): Id of the user to add into database
        """
        User.db_obj.execute("INSERT INTO user_table(user_id) VALUES (?)", (user_id,))

    @staticmethod
    def get_backend_id(user_id):
        """
        Gets the backend id of a user from the database

        Args:
            user_id (int): Id of the user to get the backend id

        Returns:
            int: The backend id of the user, or None if not found
        """
        return User.db_obj.execute(f"SELECT id FROM user_table where user_id = '{user_id}'").fetchone()
    
    
    def get_in_cart_items(user_id):
        """
        Gets all the ingredients user currently has in their cart

        Args:
            user_id (int): Id of the user to get ingreidents currently in cart

        """
        ing_list = []
        rows_objs = User.db_obj.execute(f"SELECT ingredient_id FROM user_cart_mapping where user_id = '{user_id}'").fetchall()
        for row in rows_objs:
            ing_list.append(row["ingredient_id"])

        return ing_list
    
    def delete_user_cart(user_id):
        """
        Deletes all the ingredients from the user's cart

        Args:
            user_id (int): Id of the user to delete all ingredients from cart
        """
        User.db_obj.execute(f"DELETE FROM user_cart_mapping where user_id = {user_id}")
