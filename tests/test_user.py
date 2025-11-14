"""Unit tests for services/user.py"""
import pytest
from services.user import User
from services.recipe import Recipe


class TestUser:
    """Test cases for User service."""
    
    def test_get_backend_id_exists(self, db_with_data):
        """Test getting backend ID for existing user."""
        result = User.get_backend_id(1000)
        assert result is not None
        assert result['id'] == 1
    
    def test_get_backend_id_not_exists(self, test_db):
        """Test getting backend ID for non-existent user."""
        result = User.get_backend_id(9999)
        assert result is None
    
    def test_get_by_google_sub_exists(self, db_with_data):
        """Test finding user by Google sub."""
        user_id = User.get_by_google_sub("google_123")
        assert user_id == 1000
    
    def test_get_by_google_sub_not_exists(self, test_db):
        """Test finding non-existent user by Google sub."""
        user_id = User.get_by_google_sub("nonexistent")
        assert user_id is None
    
    def test_get_by_email_exists(self, db_with_data):
        """Test finding user by email."""
        user_id = User.get_by_email("test@example.com")
        assert user_id == 1000
    
    def test_get_by_email_not_exists(self, test_db):
        """Test finding non-existent user by email."""
        user_id = User.get_by_email("nonexistent@example.com")
        assert user_id is None
    
    def test_create_with_google_first_user(self, test_db):
        """Test creating first user with Google."""
        user_id = User.create_with_google("google_new", "new@example.com", "New User")
        assert user_id == 1000
        
        # Verify user was created
        found = User.get_by_google_sub("google_new")
        assert found == 1000
    
    def test_create_with_google(self, db_with_data):
        """Test creating user with Google when users exist."""
        user_id = User.create_with_google("google_new", "new@example.com", "New User")
        assert user_id == 1001  # Next ID after 1000
        
        # Verify user was created
        found = User.get_by_google_sub("google_new")
        assert found == 1001
    
    def test_set_google_for_user(self, db_with_data):
        """Test setting Google info for existing user."""
        # Create a user without Google info first
        User.db_obj.execute("INSERT INTO user_table(user_id, google_sub, email, name) VALUES (?, ?, ?, ?)", (2000, None, None, None))
        
        # Now set Google info
        User.set_google_for_user(2000, "google_456", "user2@example.com", "User Two")
        
        # Verify it was set
        user_id = User.get_by_google_sub("google_456")
        assert user_id == 2000
    
    def test_get_in_cart_items(self, db_with_data):
        """Test getting cart items for user."""
        # Add some items to cart
        User.db_obj.execute("INSERT INTO user_cart_mapping(user_id, ingredient_id) VALUES (?, ?)", (1000, 1))
        User.db_obj.execute("INSERT INTO user_cart_mapping(user_id, ingredient_id) VALUES (?, ?)", (1000, 2))
        
        cart_items = User.get_in_cart_items(1000)
        assert len(cart_items) == 2
        assert 1 in cart_items
        assert 2 in cart_items
    
    def test_get_in_cart_items_empty(self, db_with_data):
        """Test getting cart items when cart is empty."""
        cart_items = User.get_in_cart_items(1000)
        assert len(cart_items) == 0
    
    def test_delete_user_cart(self, db_with_data):
        """Test deleting all items from user's cart."""
        # Add items to cart
        User.db_obj.execute("INSERT INTO user_cart_mapping(user_id, ingredient_id) VALUES (?, ?)", (1000, 1))
        User.db_obj.execute("INSERT INTO user_cart_mapping(user_id, ingredient_id) VALUES (?, ?)", (1000, 2))
        
        # Delete cart
        User.delete_user_cart(1000)
        
        # Verify cart is empty
        cart_items = User.get_in_cart_items(1000)
        assert len(cart_items) == 0
    
    def test_remove_selected_recipes(self, db_with_data):
        """Test removing selected recipes for user."""
        # Add some selected recipes
        User.db_obj.execute("INSERT INTO selected_meals(recipe_id, user_id) VALUES (?, ?)", (1, 1000))
        User.db_obj.execute("INSERT INTO selected_meals(recipe_id, user_id) VALUES (?, ?)", (2, 1000))
        
        # Remove selected recipes
        User.remove_selected_recipes(1000)
        
        # Verify they're gone
        result = User.db_obj.execute("SELECT COUNT(*) as count FROM selected_meals WHERE user_id = 1000").fetchone()
        assert result['count'] == 0
