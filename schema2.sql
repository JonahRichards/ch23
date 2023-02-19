DROP TABLE IF EXISTS countries;

CREATE TABLE countries (
    endpoint TEXT PRIMARY KEY,
    name TEXT,
    servings INTEGER,
    cost REAL,
    calories INTEGER,
    protein INTEGER,
    fat INTEGER,
    carbs INTEGER
);