def test_api_process(client):
    response = client.post("/process", json={"process_number": "error"})
    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert response.json["data"] == "[]"
