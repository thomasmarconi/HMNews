import json, http.client, sqlite3, requests
from os import environ as env
from urllib.parse import quote_plus, urlencode

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
    print(articles)
    return render_template("test.html", articles=articles)

@app.route("/news")
def news():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM articles').fetchall()
    conn.close()
    return render_template("news.html", data=data)

@app.route("/profile")
def profile():
    conn = get_db_connection()
    likes = conn.execute('SELECT * FROM likes').fetchall()
    dislikes = conn.execute('SELECT * FROM dislikes').fetchall()
    conn.close()
    return render_template("profile.html", session=session.get("user"),likes=likes, dislikes=dislikes)    
@app.route("/admin")
def admin():
    session = session.get("user")
    pretty = json.dumps(session.get("user"))
    
@app.route("/like", methods = ["POST","GET"])
def like():
    articleId = request.form['articleId']
    title = request.form['title']
    url = request.form['url']
    sess=session.get("user")
    connection = sqlite3.connect('database.db')
    connection.execute('INSERT OR IGNORE INTO likes (id, url, title, email) VALUES (?, ?, ?, ?)', (articleId,url,title, sess["userinfo"]["email"]))
    connection.commit()
    connection.close()
    return redirect(url_for('news'))

@app.route("/dislike", methods = ["POST","GET"])
def dislike():
    articleId = request.form['articleId'] 
    title = request.form['title']
    url = request.form['url']
    sess=session.get("user")
    connection = sqlite3.connect('database.db')
    connection.execute('INSERT OR IGNORE INTO dislikes (id, url, title, email) VALUES (?, ?, ?, ?)', (articleId,url,title, sess["userinfo"]["email"]))
    connection.commit()
    connection.close()
    return redirect(url_for('news'))

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))

