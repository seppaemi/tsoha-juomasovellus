
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE alcohols (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    tagid INTEGER REFERENCES tags,
    description TEXT,
    persentage TEXT NOT NULL,
    usage TEXT NOT NULL,
    creator_id INTEGER REFERENCES users,
    created_at TIMESTAMP DEFAULT NOW(),
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    visible INTEGER NOT NULL
);

CREATE TABLE favourites (
    id SERIAL PRIMARY KEY,
    liker_id INTEGER REFERENCES users,
    recipe_id INTEGER REFERENCES alcohols
);

CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    comment TEXT NOT NULL,
    author_id INTEGER REFERENCES users,
    alcohol_id INTEGER REFERENCES alcohols,
    created_at TIMESTAMP DEFAULT NOW(),
    visible INTEGER NOT NULL
);

CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);


CREATE TABLE photos (
    id SERIAL PRIMARY KEY,
    name TEXT, 
    data BYTEA,
    size int,
    creator_id INTEGER REFERENCES users,
    alcohol_id INTEGER REFERENCES alcohols,
    created_at TIMESTAMP DEFAULT NOW(),
    visible INTEGER NOT NULL
);
