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

    return rows

def update_ingredient(id, category, conn):
    """
    Update the category of a specific ingredient
    :param conn: the Connection object
    :param id: the ID of the ingredient
    :param category: the new category of the ingredient
    :return:
    """

    cur = conn.cursor()
    cur.execute(f'UPDATE ingredients SET category="{category}" WHERE id={id}')
    conn.commit()
    print(f"\n~~~Updated ingredient with ID: {id} to category: {category}~~~\n")



if __name__ == "__main__":

    # get the current working directory
    current_working_directory = os.getcwd()
    current_working_directory += f"/{DATABASE}"

    # create a database connection
    conn = create_connection(current_working_directory)

    ingredients = select_all_ingreidents(conn)

    for ingredient in ingredients:
        if ingredient[2] == "":
            print(f"Name: {ingredient[1]}")
            input_category = input("Enter the new category: 1: Meat, 2: Produce, 3: Dairy, 4: Other\n")
            update_ingredient(ingredient[0], input_category, conn)