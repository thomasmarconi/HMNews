from collections import Counter
from string import punctuation
from os import environ as env
from urllib.parse import quote_plus, urlencode
import json
import http.client
import sqlite3
import requests

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)
oauth.register(
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
    return render_template(
        "home.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/test")
def test():
    return "<h1>You made it to the test page</h1>"


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/logout")
def logout():
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
@app.route("/test2")
def test2():
    ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json")
    articles = []
    listids  = ids.json()
    for i in range (10):
        response = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{listids[i]}.json")
        articles.append(response.json())
    return render_template("test.html", articles=articles)

@app.route("/news")
def news():
    sess = session.get("user")
    email = sess["userinfo"]["email"]
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM articles').fetchall()
    conn.execute("INSERT OR IGNORE INTO users(email) VALUES (?)", (email,))
    conn.commit()
    conn.close()
    return render_template("news.html", data=data)

@app.route("/profile")
def profile():
    conn = get_db_connection()
    likes = conn.execute('SELECT * FROM likes').fetchall()
    dislikes = conn.execute('SELECT * FROM dislikes').fetchall()
    conn.close()
    return render_template("profile.html", session=session.get("user"), likes=likes, dislikes=dislikes)    
@app.route("/admin")
def admin():
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

@app.route("/like", methods=["POST","GET"])
def like():
    articleId = request.form['articleId']
    title = request.form['title']
    url = request.form['url']
    author = request.form['author']
    sess = session.get("user")
    email = sess["userinfo"]["email"] 
    connection = sqlite3.connect('database.db')
    cur = connection.cursor()
    res = cur.execute('SELECT * FROM likes WHERE id=(?) AND email=(?)', (articleId, email))
    if res.fetchone() is None:
        cur.execute('INSERT OR IGNORE INTO likes (id, url, title, email, author) VALUES (?, ?, ?, ?, ?)', (articleId, url, title, email, author))
    else:
        cur.execute('DELETE FROM likes WHERE id=(?) AND email=(?)', (articleId, email))
    resDis = cur.execute('SELECT * FROM dislikes WHERE id=(?) AND email=(?)', (articleId, email))
    if resDis.fetchone() is not None:
        cur.execute('DELETE FROM dislikes WHERE id=(?) AND email=(?)', (articleId, email))
    connection.commit()
    connection.close()
    return redirect(url_for('news'))

@app.route("/dislike", methods=["POST","GET"])
def dislike():
    articleId = request.form['articleId'] 
    title = request.form['title']
    url = request.form['url']
    author = request.form['author']
    sess=session.get("user")
    email = sess["userinfo"]["email"]
    connection = sqlite3.connect('database.db')
    cur = connection.cursor()
    res = cur.execute('SELECT * FROM dislikes WHERE id=(?) AND email=(?)', (articleId, email))
    if res.fetchone() is None:
        cur.execute('INSERT OR IGNORE INTO dislikes (id, url, title, email, author) VALUES (?, ?, ?, ?, ?)', (articleId, url, title, email, author))
    else:
        cur.execute('DELETE FROM dislikes WHERE id=(?) AND email=(?)',(articleId, email))
    resLik = cur.execute('SELECT * FROM likes WHERE id=(?) AND email=(?)',(articleId, email))
    if resLik.fetchone() is not None:
        cur.execute('DELETE FROM likes WHERE id=(?) AND email=(?)',(articleId, email))
    connection.commit()
    connection.close()
    return redirect(url_for('news'))

@app.route("/delete", methods=["POST", "GET"])
def delete():
    connection = sqlite3.connect('database.db')
    email = request.form['email']
    operation = request.form['operation']
    if operation == "user":
        connection.execute('DELETE FROM likes WHERE email=(?)', (email,))
        connection.execute('DELETE FROM dislikes WHERE email=(?)', (email,))
        connection.execute('DELETE FROM users WHERE email=(?)', (email,))
    elif operation == "like":
        articleId = request.form['articleId']
        connection.execute('DELETE FROM likes WHERE id=(?) AND email=(?)', (articleId, email))
    elif operation == "dislike":
        articleId = request.form['articleId']
        connection.execute('DELETE FROM dislikes WHERE id=(?) AND email=(?)', (articleId, email))
    connection.commit()
    connection.close()
    return redirect(url_for('admin'))

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def admin_email(email):
    if email == "thomas.marconi2@gmail.com":
        return True
    elif email == "jackthayes19@gmail.com":
        return True
    elif email == "piyush@gmail.com":
        return True
    elif email == "chashimahiulislam@gmail.com":
        return True
    else:
        return False

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))
