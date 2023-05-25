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
    def check_user(user_id):
        """
        Checks if a user_id exists in the database

        Args:
			user_id (int): Id of the user to check if in database
        """

        return User.db_obj.execute(f"SELECT id FROM user_table where user_id = '{user_id}'").fetchone()