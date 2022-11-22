"""news app containing all routes and functions"""
from os import environ as env
from urllib.parse import quote_plus, urlencode
import json
import sqlite3

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

OAUTH = OAuth(app)
OAUTH.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)


@app.route("/")
def home():
    """home/start page"""
    return render_template(
        "home.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )


@app.route("/login")
def login():
    """log in with auth0"""
    return OAUTH.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    """callback url for auth0 login"""
    token = OAUTH.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@app.route("/logout")
def logout():
    """logs user out through auth0"""
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/news")
def news():
    """main newsfeed, grabs articles from database"""
    sess = session.get("user")
    email = sess["userinfo"]["email"]
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM articles').fetchall()
    likes = conn.execute('SELECT * FROM likes').fetchall()
    dislikes = conn.execute('SELECT * FROM dislikes').fetchall()
    conn.execute("INSERT OR IGNORE INTO users(email) VALUES (?)", (email,))
    conn.commit()
    conn.close()
    return render_template("news.html", data=data, likes=likes, dislikes=dislikes, email=email)

@app.route("/profile")
def profile():
    """displays user profile with likes and dislikes"""
    conn = get_db_connection()
    likes = conn.execute('SELECT * FROM likes').fetchall()
    dislikes = conn.execute('SELECT * FROM dislikes').fetchall()
    conn.close()
    return render_template("profile.html", session=session.get("user"),
                           likes=likes, dislikes=dislikes)

@app.route("/admin")
def admin():
    """admin page, only accesible by certain users"""
    sess = session.get("user")
    email = sess["userinfo"]["email"]
    if not admin_email(email):
        return render_template("notAdmin.html")
    conn = get_db_connection()
    likes = conn.execute('SELECT * FROM likes').fetchall()
    dislikes = conn.execute('SELECT * FROM dislikes').fetchall()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template("admin.html", users=users, likes=likes, dislikes=dislikes)

@app.route("/like", methods=["POST", "GET"])
def like():
    """called after an item is liked to add it to database"""
    article_id = request.form['articleId']
    title = request.form['title']
    url = request.form['url']
    author = request.form['author']
    keywords = request.form['keywords']
    sess = session.get("user")
    email = sess["userinfo"]["email"]
    connection = sqlite3.connect('database.db')
    cur = connection.cursor()
    res = cur.execute('SELECT * FROM likes WHERE id=(?) AND email=(?)', (article_id, email))
    if res.fetchone() is None:
        cur.execute(
            """INSERT OR IGNORE INTO likes
            (id, url, title, email, author, keywords) VALUES (?, ?, ?, ?, ?, ?)"""
            , (article_id, url, title, email, author, keywords))
    else:
        cur.execute('DELETE FROM likes WHERE id=(?) AND email=(?)', (article_id, email))
    res_dis = cur.execute('SELECT * FROM dislikes WHERE id=(?) AND email=(?)', (article_id, email))
    if res_dis.fetchone() is not None:
        cur.execute('DELETE FROM dislikes WHERE id=(?) AND email=(?)', (article_id, email))
    connection.commit()
    connection.close()
    return redirect(url_for('news'))

@app.route("/dislike", methods=["POST", "GET"])
def dislike():
    """called after an item is disliked to add it to database"""
    article_id = request.form['articleId']
    title = request.form['title']
    url = request.form['url']
    author = request.form['author']
    keywords = request.form['keywords']
    sess = session.get("user")
    email = sess["userinfo"]["email"]
    connection = sqlite3.connect('database.db')
    cur = connection.cursor()
    res = cur.execute('SELECT * FROM dislikes WHERE id=(?) AND email=(?)', (article_id, email))
    if res.fetchone() is None:
        cur.execute(
            """INSERT OR IGNORE INTO dislikes
            (id, url, title, email, author, keywords) VALUES (?, ?, ?, ?, ?, ?)"""
            , (article_id, url, title, email, author, keywords))
    else:
        cur.execute('DELETE FROM dislikes WHERE id=(?) AND email=(?)', (article_id, email))
    res_lik = cur.execute('SELECT * FROM likes WHERE id=(?) AND email=(?)', (article_id, email))
    if res_lik.fetchone() is not None:
        cur.execute('DELETE FROM likes WHERE id=(?) AND email=(?)', (article_id, email))
    connection.commit()
    connection.close()
    return redirect(url_for('news'))

@app.route("/delete", methods=["POST", "GET"])
def delete():
    """called to delete users, likes and dislikes from database"""
    connection = sqlite3.connect('database.db')
    email = request.form['email']
    origin = request.form['origin']
    operation = request.form['operation']
    if operation == "user":
        connection.execute('DELETE FROM likes WHERE email=(?)', (email,))
        connection.execute('DELETE FROM dislikes WHERE email=(?)', (email,))
        connection.execute('DELETE FROM users WHERE email=(?)', (email,))
    elif operation == "like":
        article_id = request.form['articleId']
        connection.execute('DELETE FROM likes WHERE id=(?) AND email=(?)', (article_id, email))
    elif operation == "dislike":
        article_id = request.form['articleId']
        connection.execute('DELETE FROM dislikes WHERE id=(?) AND email=(?)', (article_id, email))
    connection.commit()
    connection.close()
    if origin == 'admin':
        return redirect(url_for('admin'))
    return redirect(url_for('profile'))

def get_db_connection():
    """initializes database connection"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def admin_email(email):
    """admin user emails"""
    if email == "thomas.marconi2@gmail.com":
        return True
    if email == "jackthayes19@gmail.com":
        return True
    if email == "piyush@gmail.com":
        return True
    if email == "chashimahiulislam@gmail.com":
        return True
    return False

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))
