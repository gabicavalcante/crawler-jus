import json

from flask import Blueprint, request

from crawler_jus.ext.db import mongo
from crawler_jus.crawler.utils import format_proc_number
from crawler_jus.crawler.run_spider import execute_spider_worker

colletion = mongo.db.process


process_blueprint = Blueprint("process", __name__, url_prefix="/")


def validate(number: str) -> bool:
    return True


@process_blueprint.route("/process", methods=["POST"])
def index():
    content = request.json

    if "process_number" in content and validate(content["process_number"]):
        number = format_proc_number(content["process_number"])
        process_data = list(colletion.find({"process_number": number}))

        if process_data:
            return (
                {
                    "status": "success",
                    "data": json.dumps([data for data in process_data], default=str),
                },
                200,
            )
        else:
            execute_spider_worker.send(number)
            return {"status": "precessing", "data": []}, 200
    return {}, 400


@process_blueprint.route("/reset", methods=["DELETE"])
def reset():
    result = colletion.delete_many({})
    return {"sucess": f"{result.deleted_count} documents deleted."}
