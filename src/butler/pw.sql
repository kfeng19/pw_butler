CREATE TABLE credential (
    id serial PRIMARY KEY,
    app_site text NOT NULL,
    salt bytea NOT NULL,
    username text,
    password text NOT NULL
);
