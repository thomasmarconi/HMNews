from os import environ as env
import pytest

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, session

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

@pytest.fixture()
def cli():
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': env.get('AUTH0_CLIENT_SECRET')
    })
    yield app

def test_news(cli):
    with cli.test_client() as client:
        with client.session_transaction() as session:
            token = OAUTH.auth0.authorize_access_token()
            session['user'] = token
        assert client.get('/news').status_code == 200
