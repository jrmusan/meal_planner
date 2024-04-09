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
        print(f"Name: {ingredient[1]}")
        input_category = input("Enter the new category: \n1: Meat\n2: Produce\n3: Dairy\n4: Other\n")
        if input_category == "1":
            input_category = "Meat"
        elif input_category == "2":
            input_category = "Produce"
        elif input_category == "3":
            input_category = "Dairy"
        elif input_category == "4":
            input_category = "Other"
        else:
            print("Invalid input. Please try again.")
            continue


        update_ingredient(ingredient[0], input_category, conn)