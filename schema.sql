DROP TABLE IF EXISTS likes;

CREATE TABLE likes(
	id TEXT PRIMARY KEY,
	url TINYTEXT,
	title TINYTEXT,
	keywords MEDIUMTEXT,
	email TINYTEXT,
	author TEXT

);

DROP TABLE IF EXISTS users;

CREATE TABLE users(
	email TINYTEXT PRIMARY KEY
);

DROP TABLE IF EXISTS dislikes;

CREATE TABLE dislikes(
	id TEXT PRIMARY KEY,
	url TINYTEXT,
	title TINYTEXT,
	keywords MEDIUMTEXT,
	email TINYTEXT,
	author TEXT
);

DROP TABLE IF EXISTS articles;

CREATE TABLE articles(
	id TEXT PRIMARY KEY,
	url TEXT,
	title TEXT,
	author TEXT
);
