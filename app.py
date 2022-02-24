#!/usr/bin/env python3

import sqlite3
from flask import Flask, render_template
from werkzeug.exceptions import abort

# This will return a database connection to our SQLite db
# This will return rows from the db that are just dicts
def get_db_connection():
	conn = sqlite3.connect('database.db')
	conn.row_factory = sqlite3.Row
	return conn

def get_post(post_id):
	conn = get_db_connection()
	post = conn.execute('SELECT * FROM posts WHERE id = ?',
						(post_id,)).fetchone()
	conn.close()
	if post is None:
		abort(404)
	return post

app = Flask(__name__)

# This is just for the base home page route
@app.route('/')
def index():
	
	# This willn open the db connection
	conn = get_db_connection()
	
	# Next we select all entries in the (posts) table
	posts = conn.execute('SELECT * FROM posts').fetchall()
	conn.close()
	return render_template('index.html', posts=posts)


# This is our route to see a post
@app.route('/<int:post_id>')
def post(post_id):
	post = get_post(post_id)
	return render_template('recipe.html', post=post)