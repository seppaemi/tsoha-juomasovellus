CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    role INTEGER
);

CREATE TABLE alcohols (
    id SERIAL PRIMARY KEY,
    creator_id INTEGER REFERENCES users,
    created_at TIMESTAMPTZ,
    viewed INTEGER,
    title TEXT,
    description TEXT,
    notes TEXT,
    visible INTEGER
);

CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    alcohol_id INTEGER REFERENCES alcohols,
    notes TEXT,
    visible INTEGER
);

CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    tag TEXT
);

CREATE TABLE alcoholtags (
    alcohol_id INTEGER REFERENCES alcohols,
    tag_id INTEGER REFERENCES tags,
    visible INTEGER
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    alcohol_id INTEGER REFERENCES alcohols,
    sender_id INTEGER REFERENCES users,
    comment TEXT,
    sent_at TIMESTAMPTZ,
    visible INTEGER
);

CREATE TABLE grades (
    id SERIAL PRIMARY KEY,
    alcohol_id INTEGER REFERENCES alcohols,
    grade INTEGER,
    visible INTEGER
);

CREATE TABLE favourites (
    user_id INTEGER REFERENCES users,
    alcohol_id INTEGER REFERENCES alcohols,
    added TIMESTAMPTZ,
    visible INTEGER
);