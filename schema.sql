DROP TABLE IF EXISTS endpoints;

CREATE TABLE endpoints (
    endpoint TEXT PRIMARY KEY
);

DROP TABLE IF EXISTS recipes;

CREATE TABLE recipes (
    endpoint TEXT PRIMARY KEY,
    name TEXT,
    servings INTEGER,
    cost REAL,
    cost_serving REAL,
    calories INTEGER,
    protein INTEGER,
    fat INTEGER,
    carbs INTEGER
);

DROP TABLE IF EXISTS ingredients;

CREATE TABLE ingredients (
    endpoint TEXT PRIMARY KEY,
    ingredient TEXT,
    cost REAL
);