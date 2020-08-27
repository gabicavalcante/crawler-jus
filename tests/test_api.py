import json
import mock


def test_api(client):
    with mock.patch("crawler_jus.database.db") as mock_mongo:
        response = client.post(
            "/process", json={"process_number": "0821901-51.2018.8.12.0001"}
        )
        assert response.status_code == 200
        assert response.json["status"] == "processing"
        assert response.json["data"] == []


def test_api_with_valid_process_number(client):
    with mock.patch("crawler_jus.database.db") as mock_mongo:
        response = client.post(
            "/process", json={"process_number": "0710802-55.2018.8.02.0001"}
        )
        assert response.status_code == 200
        assert response.json["status"] == "success"
        assert len(json.loads(response.json["data"])) == 1


def test_validate(client):
    from crawler_jus.api.process import validate

    assert validate("0710802-55.2018.8.02.0001")
    assert validate("0821901-51.2018.8.12.0001")
    assert not validate("1111111111111111")
