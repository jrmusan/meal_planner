#!/usr/bin/env python3
"""
Delete Google User Script
Removes a user and all their associated data from the database
so they can sign up again as a "new" user.
"""

import sys
import os

# Add parent directory to path so we can import database module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

def delete_user(email):
    """Delete a user by their email address."""
    db = Database()
    
    # First, find the user
    user_row = db.execute("SELECT user_id, google_sub, email, name FROM user_table WHERE email = ?", (email,)).fetchone()
    
    if not user_row:
        print(f"❌ No user found with email: {email}")
        return False
    
    user_id = user_row['user_id']
    print(f"\n👤 Found user:")
    print(f"   User ID: {user_id}")
    print(f"   Email: {user_row['email']}")
    print(f"   Name: {user_row['name']}")
    print(f"   Google Sub: {user_row['google_sub']}")
    
    # Confirm deletion
    print(f"\n⚠️  This will delete:")
    print(f"   - The user account")
    print(f"   - All their recipes")
    print(f"   - All their meal plans")
    print(f"   - Their shopping cart")
    
    response = input(f"\n❓ Are you sure you want to delete this user? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Deletion cancelled")
        return False
    
    # Delete user data in order (respecting foreign keys)
    print("\n🗑️  Deleting user data...")
    
    # 1. Delete from shopping cart
    db.execute("DELETE FROM user_cart_mapping WHERE user_id = ?", (user_id,))
    print("   ✓ Deleted shopping cart items")
    
    # 2. Delete selected meals
    db.execute("DELETE FROM selected_meals WHERE user_id = ?", (user_id,))
    print("   ✓ Deleted meal plan selections")
    
    # 3. Get all recipe IDs for this user
    recipes = db.execute("SELECT id FROM recipes WHERE user_id = ?", (user_id,)).fetchall()
    recipe_ids = [r['id'] for r in recipes]
    
    if recipe_ids:
        # 4. Delete menu_map entries for user's recipes
        for recipe_id in recipe_ids:
            db.execute("DELETE FROM menu_map WHERE recipe_id = ?", (recipe_id,))
        print(f"   ✓ Deleted {len(recipe_ids)} recipe ingredient mappings")
        
        # 5. Delete all recipes for this user
        db.execute("DELETE FROM recipes WHERE user_id = ?", (user_id,))
        print(f"   ✓ Deleted {len(recipe_ids)} recipes")
    else:
        print("   ✓ No recipes to delete")
    
    # 6. Finally, delete the user
    db.execute("DELETE FROM user_table WHERE user_id = ?", (user_id,))
    print("   ✓ Deleted user account")
    
    print(f"\n✅ User {email} has been completely removed!")
    print("   They can now sign up again as a new user.")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Google User Deletion Tool")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = input("\nEnter the email address of the user to delete: ")
    
    if not email:
        print("❌ Email is required")
        sys.exit(1)
    
    success = delete_user(email)
    sys.exit(0 if success else 1)
