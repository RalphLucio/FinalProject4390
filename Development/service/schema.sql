CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    hash TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL,
    predicted BOOL NOT NULL DEFAULT 0,
    cancer_pred FLOAT NOT NULL DEFAULT 0.0
);