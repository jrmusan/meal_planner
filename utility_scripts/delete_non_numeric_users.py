#!/usr/bin/env python3
"""
Script to delete all non-numeric user IDs from the database.
This will remove users and all their associated data (recipes, meal plans, etc.)
"""

import sys
import os

# Add parent directory to path so we can import database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

def delete_non_numeric_users():
    """Delete all users with non-numeric user_ids and their associated data."""
    
    db = Database()
    
    # First, find all non-numeric user_ids
    query = "SELECT user_id FROM user_table WHERE user_id NOT GLOB '[0-9]*'"
    non_numeric_users = db.execute(query).fetchall()
    
    if not non_numeric_users:
        print("No non-numeric user IDs found.")
        return
    
    print(f"Found {len(non_numeric_users)} non-numeric user IDs:")
    for row in non_numeric_users:
        print(f"  - {row['user_id']}")
    
    # Ask for confirmation
    response = input("\nAre you sure you want to delete these users and ALL their data? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return
    
    # Delete all associated data for each non-numeric user
    deleted_count = 0
    for row in non_numeric_users:
        user_id = row['user_id']
        print(f"\nDeleting user '{user_id}' and all associated data...")
        
        try:
            # Delete from all related tables
            db.execute("DELETE FROM recipe WHERE user_id = ?", (user_id,))
            db.execute("DELETE FROM meal_plan WHERE user_id = ?", (user_id,))
            db.execute("DELETE FROM selected_meals WHERE user_id = ?", (user_id,))
            db.execute("DELETE FROM user_cart_mapping WHERE user_id = ?", (user_id,))
            db.execute("DELETE FROM user_table WHERE user_id = ?", (user_id,))
            
            deleted_count += 1
            print(f"  ✓ Deleted user '{user_id}'")
        except Exception as e:
            print(f"  ✗ Error deleting user '{user_id}': {e}")
    
    print(f"\n{'='*50}")
    print(f"Successfully deleted {deleted_count} user(s)")
    print(f"{'='*50}")

if __name__ == "__main__":
    delete_non_numeric_users()
