import sqlite3
import os

DATABASE = "database.db"

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None

    try:
        conn = sqlite3.connect(db_file)
        print("~~~Got a db connection~~~\n")
        return conn
    except Exception as e:
        print(e)

    return 

def select_all_ingreidents(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute('SELECT * FROM ingredients')

    rows = cur.fetchall()

    for row in rows:
        print(f"Name: {row[1]} ID: {row[0]}")

def delete_specific_ingredient(conn, id):
    """
    Delete a specific ingredient by ID
    :param conn: the Connection object
    :param id: the ID of the ingredient
    :return:
    """

    # First make sure this ingredient isn't being used in any recipes
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM recipes WHERE id={id}')
    rows = cur.fetchall()

    if len(rows) > 0:
        print(f"\n~~~Ingredient with ID: {id} is being used in a recipe. Cannot delete~~~\n)
        return
    else:
        cur.execute(f'\n~~~DELETE FROM ingredients WHERE id={id}~~~/n')
        conn.commit()
        print(f"Deleted ingredient with ID: {id}")

def get_user_input(conn):
        
    print("\n1: List all ingreidents \n2: Delete specific ingrediet (Provide ID)\n3: Exit\n")
    to_do = input("What would you like to do? ")
    return int(to_do)


if __name__ == "__main__":

    # get the current working directory
    current_working_directory = os.getcwd()
    current_working_directory += f"/{DATABASE}"

    # create a database connection
    conn = create_connection(current_working_directory)

    to_do = get_user_input(conn)

    while to_do != 3:
        if to_do == 1:
            print("Here are all the ingredients: \n")
            select_all_ingreidents(conn)
            to_do = get_user_input(conn)
            
        elif to_do == 2:
            delete_specific_ingredient(conn, input("Enter the ID of the ingredient you would like to delete "))
            to_do = get_user_input(conn)

        elif to_do == 3:
            conn.close()
            print("Exiting...")
            break
