
DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS Alcohols CASCADE;
DROP TABLE IF EXISTS Favorites CASCADE;
DROP TABLE IF EXISTS Review CASCADE;

CREATE TABLE IF NOT EXISTS Users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE CHECK(username IS NOT NULL AND length(username) > 3),
    password TEXT CHECK(password IS NOT NULL AND length(password) > 7),
    role INTEGER
);

CREATE TABLE IF NOT EXISTS Alcohols (
    id SERIAL PRIMARY KEY,
    alcohol_name TEXT UNIQUE,
    description TEXT,
    presentages TEXT
    alcohol_type TEXT
);

CREATE TABLE IF NOT EXISTS Favorites (
    user_id INTEGER REFERENCES Users (id) ON DELETE CASCADE,
    alcohol_id INTEGER REFERENCES Alcohols (id) ON DELETE CASCADE,
    UNIQUE(user_id, alcohol_id)
);

CREATE TABLE Review (
    id SERIAL PRIMARY KEY,
    rating INTEGER,
    comment TEXT,
    user_id INTEGER REFERENCES Users(id) ON DELETE CASCADE,
    alcohol_id INTEGER REFERENCES Alcohols (id) ON DELETE CASCADE,
    sent_at TIMESTAMP
);