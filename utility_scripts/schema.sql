
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
    times_used INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES user_table(id)
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
    user_id INTEGER
);

CREATE TABLE IF NOT EXISTS user_cart_mapping (
    user_id INTEGER,
    ingredient_id INTEGER,
    PRIMARY KEY(user_id. ingredient_id)
);
