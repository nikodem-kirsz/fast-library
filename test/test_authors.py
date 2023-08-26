import requests

from helpers import create_author


def test_add_authors(app):
    assert create_author("Arthur C. Clarke") == 1
    assert create_author("Stephen Hawking") == 2


def test_get_authors(app):
    create_author("Arthur C. Clarke")
    create_author("Stephen Hawking")

    response = requests.get("http://127.0.0.1:8000/v1/authors")
    assert response.status_code == 200
    assert response.json() == {
        "authors": [
            {"id": 1, "name": "Arthur C. Clarke"},
            {"id": 2, "name": "Stephen Hawking"}
        ]
    }


def test_get_author(app):
    author_id = create_author("Arthur C. Clarke")

    response = requests.get(f"http://127.0.0.1:8000/v1/authors/{author_id}")
    assert response.status_code == 200
    assert response.json() == {"id": author_id, "title": "Arthur C. Clarke"}

    response = requests.get("http://127.0.0.1:8000/v1/authors/2")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Author not found'}
