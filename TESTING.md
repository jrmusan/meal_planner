# Quick Test Reference

## Install Test Dependencies
```bash
pip install pytest pytest-cov
```

## Run Tests

### Simple run:
```bash
./run_tests.sh
```

### Or with pytest directly:
```bash
pytest
```

### View HTML coverage report:
```bash
open htmlcov/index.html
```

## What's Tested

✅ **User Service** (22 tests)
- User creation with Google OAuth
- User lookup by Google sub and email
- Cart management
- Selected recipes management

✅ **Recipe Service** (18 tests)
- Recipe CRUD operations
- Meal plan management
- Recipe copying between users
- Times used tracking
- Ingredient updates

✅ **Ingredient Service** (11 tests)
- Ingredient listing and retrieval
- Ingredient creation
- Ingredient combining across recipes
- JSON serialization

## Expected Results

All 51 tests should pass with coverage report showing:
- Coverage percentage for each service file
- Lines not covered (if any)
- Branch coverage statistics

## Troubleshooting

If tests fail:
1. Check that the database schema is up to date
2. Verify all service methods match the test expectations
3. Review test output for specific assertion failures
4. Use `pytest -v` for verbose output with individual test results
