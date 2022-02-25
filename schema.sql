DROP TABLE IF EXISTS posts;

CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE recipe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE menu_map (
    FOREIGN KEY(ingredient_id) REFERENCES ingredients(id),
    FOREIGN KEY(recipe_id) REFERENCES recipe(id),
    quantity INTEGER NOT NULL,
    unit TEXT
);

