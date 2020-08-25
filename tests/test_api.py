import json
import pytest
from mock import patch
from crawler_jus.ext.db import mongo


def test_api(client):
    response = client.post("/process", json={"process_number": "error"})
    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert response.json["data"] == "[]"


def test_api_process(client, mongo):
    response = client.post("/process", json={"process_number": "08219015120188120001"})
    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert len(json.loads(response.json["data"])) == 1
