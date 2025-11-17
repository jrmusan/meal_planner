from database import Database
from services.recipe import Recipe

class User:

    db_obj = Database()
	
    def __init__(self, user_id):

        self.user_id = user_id

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

    def remove_selected_recipes(user_id):
        """
        Removes all the selected meals for this user 

        Args:
            user_id (int): Id of the user to get selected recipes for
        """
        
        User.db_obj.execute(f"DELETE FROM selected_meals where user_id = {user_id}")

    @staticmethod
    def get_by_google_sub(google_sub):
        """Return the user_id for a given google_sub, or None"""
        row = User.db_obj.execute("SELECT user_id FROM user_table WHERE google_sub = ?", (google_sub,)).fetchone()
        return row['user_id'] if row else None

    @staticmethod
    def get_by_email(email):
        row = User.db_obj.execute("SELECT user_id FROM user_table WHERE email = ?", (email,)).fetchone()
        return row['user_id'] if row else None

    @staticmethod
    def set_google_for_user(user_id, google_sub, email=None, name=None):
        """Associate an existing local user_id with a Google account"""
        User.db_obj.execute("UPDATE user_table SET google_sub = ?, email = ?, name = ? WHERE user_id = ?", (google_sub, email, name, user_id))

    @staticmethod
    def create_with_google(google_sub, email=None, name=None):
        """Create a new local user and associate Google info. Generates a new numeric user_id.

        Returns the new user_id.
        """
        # Generate a new numeric user_id: max(user_id) + 1
        row = User.db_obj.execute("SELECT MAX(user_id) as maxid FROM user_table").fetchone()
        new_user_id = int(row['maxid']) + 1 if row and row['maxid'] is not None else 1000
        
        User.db_obj.execute("INSERT INTO user_table(user_id, google_sub, email, name) VALUES (?, ?, ?, ?)", (new_user_id, google_sub, email, name))
        
        # Add default recipes for the new user and add them to their meal plan
        default_recipe_ids = [3, 93, 86]
        for recipe_id in default_recipe_ids:
            new_recipe_id = Recipe.copy_recipe_for_user(recipe_id, new_user_id)
            # Also add the copied recipe to their meal plan
            Recipe.add_to_meal_plan(new_recipe_id, new_user_id)
            
        return new_user_id