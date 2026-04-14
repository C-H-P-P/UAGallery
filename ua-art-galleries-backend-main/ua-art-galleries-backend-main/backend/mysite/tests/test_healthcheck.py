import requests

def test_healthcheck_returns_200():
    url = "http://localhost:8000/api/galleries/"
    response = requests.get(url)

    assert response.status_code == 200
    assert response.text != ""



#python -m pytest
