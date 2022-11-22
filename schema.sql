CREATE TABLE IF NOT EXISTS articles(
        id TEXT PRIMARY KEY,
        url TEXT,
        title TEXT,
        author TEXT,
        keywords MEDIUMTEXT
);

CREATE TABLE IF NOT EXISTS tempArticles(
        id TEXT PRIMARY KEY,
        url TEXT,
        title TEXT,
        author TEXT,
        keywords MEDIUMTEXT
);

INSERT OR IGNORE INTO tempArticles SELECT * FROM articles;

DROP TABLE IF EXISTS articles;

CREATE TABLE IF NOT EXISTS articles(
        id TEXT PRIMARY KEY,
        url TEXT,
        title TEXT,
        author TEXT,
        keywords MEDIUMTEXT
);
