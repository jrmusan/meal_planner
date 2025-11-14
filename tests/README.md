# Test Suite for Meal Planner

This directory contains unit tests for the meal planner service layers.

## Setup

Install the required testing dependencies:

```bash
pip install pytest pytest-cov
```

Or add to your `requirements.txt`:
```
pytest==7.4.3
pytest-cov==4.1.0
```

## Running Tests

### Run all tests with coverage:
```bash
./run_tests.sh
```

Or directly with pytest:
```bash
pytest
```

### Run specific test file:
```bash
pytest tests/test_user.py
```

### Run specific test:
```bash
pytest tests/test_user.py::TestUser::test_get_backend_id_exists
```

### Run with verbose output:
```bash
pytest -v
```

### Run without coverage:
```bash
pytest --no-cov
```

## Coverage Reports

After running tests, coverage reports are generated in two formats:

1. **Terminal output**: Shows coverage summary with missing lines
2. **HTML report**: Interactive report in `htmlcov/index.html`

To view the HTML report:
```bash
open htmlcov/index.html
```

## Test Structure

- `conftest.py`: Pytest fixtures and configuration
- `test_user.py`: Tests for `services/user.py`
- `test_recipe.py`: Tests for `services/recipe.py`
- `test_ingredient.py`: Tests for `services/ingredient.py`

## Fixtures

### `test_db`
Creates a temporary SQLite database with the schema for testing.

### `db_with_data`
Creates a temporary database pre-populated with sample data including:
- 2 users
- 3 ingredients
- 3 recipes
- Sample recipe-ingredient mappings
- Sample selected meals

## Writing New Tests

Follow these conventions:

1. Create test classes with `Test` prefix
2. Name test methods with `test_` prefix
3. Use descriptive test names: `test_<method>_<scenario>`
4. Use fixtures for database setup
5. Clean up after tests (fixtures handle this automatically)

Example:
```python
def test_method_name_scenario(self, db_with_data):
    """Test description."""
    # Arrange
    expected = "value"
    
    # Act
    result = Method.call()
    
    # Assert
    assert result == expected
```

## CI/CD Integration

To integrate with CI/CD pipelines:

```yaml
# Example for GitHub Actions
- name: Run tests
  run: |
    pip install pytest pytest-cov
    pytest --cov=services --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
```
