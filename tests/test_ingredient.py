"""Unit tests for services/ingredient.py"""
import pytest
from services.ingredient import Ingredent
from services.recipe import Recipe


class TestIngredient:
    """Test cases for Ingredent service."""
    
    def test_list_ingredients(self, db_with_data):
        """Test listing all ingredients."""
        ingredients = Ingredent.list_ingredients()
        
        assert len(ingredients) == 3
        # Check that ingredients are returned as objects
        assert all(isinstance(ing, Ingredent) for ing in ingredients)
        ingredient_names = [ing.name for ing in ingredients]
        assert "Chicken" in ingredient_names
        assert "Rice" in ingredient_names
        assert "Broccoli" in ingredient_names
    
    def test_list_ingredients_empty(self, test_db):
        """Test listing ingredients when database is empty."""
        ingredients = Ingredent.list_ingredients()
        assert len(ingredients) == 0
    
    def test_get_ingredient(self, db_with_data):
        """Test getting a specific ingredient."""
        # get_ingredient takes (id, quantity, unit)
        ingredient = Ingredent.get_ingredient(1, 2, "pound")
        
        assert ingredient is not None
        assert ingredient.id == 1
        assert ingredient.name == "Chicken"
        assert ingredient.category == "Protein"
        assert ingredient.quantity == 2
        assert ingredient.unit == "pound"
    
    def test_get_ingredient_not_found(self, db_with_data):
        """Test getting non-existent ingredient."""
        # This will raise an error if ingredient doesn't exist
        # because it tries to access ingredient_row['name'] on None
        with pytest.raises(TypeError):
            Ingredent.get_ingredient(9999, 1, "item")
    
    def test_insert_ingredient(self, test_db):
        """Test inserting a new ingredient."""
        ingredient = Ingredent(name="Tomato", category="Vegetable")
        ingredient.insert_ingredient()
        
        # Verify ingredient was created
        ingredients = Ingredent.list_ingredients()
        assert len(ingredients) == 1
        assert ingredients[0].name == "Tomato"
        assert ingredients[0].category == "Vegetable"
    
    def test_ingredient_combiner(self, db_with_data):
        """Test combining ingredients from multiple recipes."""
        recipe1 = Recipe.get_recipe(1)
        recipe2 = Recipe.get_recipe(2)
        recipes = [recipe1, recipe2]
        
        combined = Ingredent.ingredient_combiner(recipes)
        
        # Both recipes use Chicken and Rice, so they should be combined
        chicken = [ing for ing in combined if ing.name == "Chicken"][0]
        rice = [ing for ing in combined if ing.name == "Rice"][0]
        
        # Recipe 1: 2 lbs chicken, 1 cup rice, 2 cups broccoli
        # Recipe 2: 1 lb chicken, 2 cups rice
        # Combined: 3 lbs chicken, 3 cups rice, 2 cups broccoli
        assert chicken.quantity == 3
        assert chicken.unit == "pound"
        assert rice.quantity == 3
        assert rice.unit == "cup"
    
    def test_ingredient_json_property(self, db_with_data):
        """Test ingredient JSON property."""
        ingredient = Ingredent.get_ingredient(1, 1, "item")
        json_data = ingredient.json
        assert json_data["name"] == "Chicken"
        assert json_data["id"] == 1
    
    def test_ingredient_repr(self, db_with_data):
        """Test ingredient string representation."""
        ingredient = Ingredent.get_ingredient(1, 1, "item")
        assert str(ingredient) == "Chicken"
    
    def test_set_ingredient_as_selected(self, db_with_data):
        """Test setting an ingredient as selected for a user."""
        Ingredent.set_ingredient_as_selected(1, 1000)
        
        # Verify it was added to cart
        from services.user import User
        cart_items = User.get_in_cart_items(1000)
        assert 1 in cart_items
