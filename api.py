from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def index():
    content = request.json
    if "number" in content:
        return {"sucess": content.get("number")}
    return {}, 400
