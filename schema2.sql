DROP TABLE IF EXISTS countries;

CREATE TABLE countries (
    country TEXT PRIMARY KEY,
    currency TEXT,
    rate REAL,
    food_inx REAL,
    grain_inx REAL,
    meat_inx REAL,
    fish_inx REAL,
    dairy_inx REAL,
    oil_inx REAL,
    fruit_inx REAL,
    veg_inx REAL,
    sweets_inx REAL,
    bev_inx REAL,
    alcohol_inx REAL
);