CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT
);

CREATE TABLE alcohols (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE,
    user_id INTEGER REFERENCES users,
    description TEXT,
    persentage DECIMAL
    average_rating FLOAT
);

CREATE TABLE favorites (
    user_id INTEGER REFERENCES users,
    alcohol_id INTEGER REFERENCES alcohols
);

CREATE TABLE tag (
    id SERIAL PRIMARY KEY,
    name TEXT,
    alcohol_id INTEGER REFERENCES alcohols ON DELETE CASCADE
);

CREATE TABLE review (
    id SERIAL PRIMARY KEY,
    rating INTEGER,
    comment TEXT,
    user_id INTEGER REFERENCES users (id) ON DELETE CASCADE,
    alcohol_id INTEGER REFERENCES alcohols (id) ON DELETE CASCADE,
    sent_at TIMESTAMP
);