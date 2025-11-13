import sqlite3

# Connect to the database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Get the table information
cursor.execute("PRAGMA table_info(user_table)")
columns = [row[1] for row in cursor.fetchall()]

# Add the google_sub column if it doesn't exist
if 'google_sub' not in columns:
    cursor.execute("ALTER TABLE user_table ADD COLUMN google_sub TEXT")
    print("Added 'google_sub' column to 'user_table'")

# Add the email column if it doesn't exist
if 'email' not in columns:
    cursor.execute("ALTER TABLE user_table ADD COLUMN email TEXT")
    print("Added 'email' column to 'user_table'")

# Add the name column if it doesn't exist
if 'name' not in columns:
    cursor.execute("ALTER TABLE user_table ADD COLUMN name TEXT")
    print("Added 'name' column to 'user_table'")

# Commit the changes and close the connection
conn.commit()
conn.close()
