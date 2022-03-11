
CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    notes TEXT,
    cuisine TEXT
);

CREATE TABLE menu_map (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_id INTEGER,
    recipe_id INTEGER,
    quantity INTEGER NOT NULL,
    unit TEXT,
    FOREIGN KEY(ingredient_id) REFERENCES ingredients(id),
    FOREIGN KEY(recipe_id) REFERENCES recipes(id)
);

CREATE TABLE selected_meals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id)
);
