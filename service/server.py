from flask import Flask

from service import Service

app = Flask(__name__)
service = Service()


@app.route("/")
def hello():
    return "Hello World!"
