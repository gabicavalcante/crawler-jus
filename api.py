from flask import Flask, request

app = Flask(__name__)


def validate(number: str) -> bool:
    return True


@app.route("/")
def index():
    content = request.json
    if "number" in content and validate(content["number"]):
        return {"sucess": content.get("number")}
    return {}, 400
