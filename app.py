#!/usr/bin/env python3

import sqlite3
from flask import Flask, render_template

# This will return a database connection to our SQLite db
# This will return rows from the db that are just dicts
def get_db_connection():
	conn = sqlite3.connect('database.db')
	conn.row_factory = sqlite3.Row
	return conn

app = Flask(__name__)

@app.route('/')
def index():
	
	# This willn open the db connection
	conn = get_db_connection()
	
	# Next we select all entries in the (posts) table
	posts = conn.execute('SELECT * FROM posts').fetchall()
	conn.close()
	return render_template('index.html', posts=posts)
