import json, http.client
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for

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


@app.route("/news")
def news():
    conn = http.client.HTTPSConnection("hacker-news.firebaseio.com")
    payload = "[]"
    conn.request("GET", "/v0/topstories.json?print=pretty", payload)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    data = data[2:len(data)-2]
    data = data.split(", ")
    data = [int(x) for x in data]
    conn.close()
    data2 = []
    for x in range(10):
        conn.request("GET", "/v0/item/{}.json?print=pretty".format(data[x]), payload)
        res2 = conn.getresponse()
        data2.append(res2.read().decode("utf-8"))
        conn.close()   
    return render_template("news.html", data2=data2)

# allows us to do 'python hello.py' and we dont have to set env variables and do flask run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))