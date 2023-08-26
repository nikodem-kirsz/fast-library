import requests

from helpers import create_reader


def test_add_readers(app):
    assert create_reader("Nikodem") == 1
    assert create_reader("Marta") == 2


def test_get_readers(app):
    create_reader("Nikodem")
    create_reader("Marta")

    response = requests.get("http://127.0.0.1:8000/v1/readers")

    assert response.json() == {
        "readers": [
            {"id": 1, "name": "Nikodem"},
            {"id": 2, "name": "Marta"}
        ]
    }


def test_get_reader(app):
    reader_id = create_reader("Nikodem")

    response = requests.get(f"http://127.0.0.1:8000/v1/readers/{reader_id}")
    assert response.status_code == 200
    assert response.json() == {"id": reader_id, "name": "Nikodem"}

    response = requests.get("http://127.0.0.1:8000/v1/readers/2")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Reader not found'}
