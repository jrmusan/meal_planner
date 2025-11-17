"""Pytest configuration and fixtures for meal_planner tests."""
import pytest
import sqlite3
import os
import tempfile
from database import Database
from services.user import User
from services.recipe import Recipe
from services.ingredient import Ingredent


@pytest.fixture
def test_db():
    """Create a temporary test database."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Set up the test database with schema
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Create tables based on schema
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            notes TEXT,
            cuisine TEXT, 
            user_id INTEGER,
            times_used INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS menu_map (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ingredient_id INTEGER,
            recipe_id INTEGER,
            quantity INTEGER NOT NULL,
            unit TEXT,
            FOREIGN KEY(ingredient_id) REFERENCES ingredients(id),
            FOREIGN KEY(recipe_id) REFERENCES recipes(id)
        );

        CREATE TABLE IF NOT EXISTS selected_meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER, 
            user_id INTEGER, 
            FOREIGN KEY(recipe_id) REFERENCES recipes(id), 
            FOREIGN KEY(user_id) REFERENCES user_table(id)
        );

        CREATE TABLE IF NOT EXISTS user_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INTEGER,
            google_sub TEXT,
            email TEXT,
            name TEXT
        );

        CREATE TABLE IF NOT EXISTS user_cart_mapping (
            user_id INTEGER,
            ingredient_id INTEGER,
            PRIMARY KEY(user_id, ingredient_id)
        );
    """)
    
    conn.commit()
    conn.close()
    
    # Create a new Database instance for testing by temporarily modifying __init__
    original_init = Database.__init__
    
    def test_init(self):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    Database.__init__ = test_init
    
    # Create test database instances
    test_db_instance = Database()
    
    # Override the class-level db_obj for all service classes
    original_user_db = User.db_obj
    original_recipe_db = Recipe.db_obj
    original_ingredient_db = Ingredent.db_obj
    
    User.db_obj = test_db_instance
    Recipe.db_obj = test_db_instance
    Ingredent.db_obj = test_db_instance
    
    yield db_path
    
    # Restore original database connections
    User.db_obj = original_user_db
    Recipe.db_obj = original_recipe_db
    Ingredent.db_obj = original_ingredient_db
    
    # Restore original __init__
    Database.__init__ = original_init
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def db_with_data(test_db):
    """Create a test database with sample data."""
    conn = sqlite3.connect(test_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Insert sample users
    cursor.execute("INSERT INTO user_table (user_id, google_sub, email, name) VALUES (1000, 'google_123', 'test@example.com', 'Test User')")
    cursor.execute("INSERT INTO user_table (user_id) VALUES (2000)")
    
    # Insert sample ingredients
    cursor.execute("INSERT INTO ingredients (name, category) VALUES ('Chicken', 'Protein')")
    cursor.execute("INSERT INTO ingredients (name, category) VALUES ('Rice', 'Grain')")
    cursor.execute("INSERT INTO ingredients (name, category) VALUES ('Broccoli', 'Vegetable')")
    
    # Insert sample recipes
    cursor.execute("INSERT INTO recipes (name, notes, cuisine, user_id, times_used) VALUES ('Chicken Stir Fry', 'Easy dinner', 'Asian', 1000, 5)")
    cursor.execute("INSERT INTO recipes (name, notes, cuisine, user_id, times_used) VALUES ('Chicken wings', 'Simple meal', 'Asian', 1000, 2)")
    cursor.execute("INSERT INTO recipes (name, notes, cuisine, user_id, times_used) VALUES ('Other User Recipe', 'Test', 'Italian', 2000, 0)")
    
    # Insert recipe ingredients (menu_map)
    # Recipe 1 (Chicken Stir Fry): 2 lbs chicken, 1 cup rice, 2 cups broccoli
    cursor.execute("INSERT INTO menu_map (ingredient_id, recipe_id, quantity, unit) VALUES (1, 1, 2, 'pound')")
    cursor.execute("INSERT INTO menu_map (ingredient_id, recipe_id, quantity, unit) VALUES (2, 1, 1, 'cup')")
    cursor.execute("INSERT INTO menu_map (ingredient_id, recipe_id, quantity, unit) VALUES (3, 1, 2, 'cup')")
    
    # Recipe 2 (Chicken wings): 1 lb chicken, 2 cups rice
    cursor.execute("INSERT INTO menu_map (ingredient_id, recipe_id, quantity, unit) VALUES (1, 2, 1, 'pound')")
    cursor.execute("INSERT INTO menu_map (ingredient_id, recipe_id, quantity, unit) VALUES (2, 2, 2, 'cup')")
    
    conn.commit()
    conn.close()
    
    return test_db
