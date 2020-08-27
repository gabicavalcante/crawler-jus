import json

from flask import Blueprint, request

from crawler_jus.database import db
from crawler_jus.crawler.utils import format_proc_number
from crawler_jus.crawler.run_spider import execute_spider_worker

process_blueprint = Blueprint("process", __name__, url_prefix="/")


def validate(number: str) -> bool:
    if len(number) == 25:
        value = "%s%s00" % (number[:7], number[10:].replace(".", ""))
        digito_verificador = 98 - (int(value) % 97)
        if digito_verificador == int(number[8:10]):
            return True
    return False


@process_blueprint.route("/process", methods=["POST"])
def index():
    content = request.json

    if "process_number" in content and validate(content["process_number"]):
        number = format_proc_number(content["process_number"])
        process_data = list(db.process.find({"process_number": number}))

        if process_data:
            return (
                {
                    "status": "success",
                    "data": json.dumps([data for data in process_data], default=str),
                },
                200,
            )
        else:
            execute_spider_worker(number, subprocess=True)
            return {"status": "processing", "data": []}, 200
    return {}, 422


@process_blueprint.route("/reset", methods=["DELETE"])
def reset():
    result = db.process.delete_many({})
    return {"sucess": f"{result.deleted_count} documents deleted."}
