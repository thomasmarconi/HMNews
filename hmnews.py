
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hell_world():
    return "<h1>Hello World! Welcome to HMNews." #</h1><iframe> src="https://giphy.com/embed/xUPGGDNsLvqsBOhuU0" width="480" height="360" frameBorder="0" class="giphy-embed" allowFullScreen></iframe>"

@app.route("/test")
def test():
    return "<h1>Test Page!</h1>"

#allows us to do 'python hello.py' and we dont have to set env variables and do flask run
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
