DROP TABLE IF EXISTS user;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

DROP TABLE IF EXISTS simulations;

CREATE TABLE simulations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sim_name TEXT NOT NULL,
  sim_description TEXT ,
  db_path TEXT NOT NULL,
  user_id integer NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id)
);
