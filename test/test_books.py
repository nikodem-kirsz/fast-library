import requests
from helpers import create_author, create_book


def test_add_books(app):
    author_id = create_author("Stephen Hawking")

    response = create_book(author_id, "Short story of universe")
    assert response.status_code == 201
    assert response.ok
    assert response.json() == {'book_id': 1}

    response = create_book(2, "Non existing's author book")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Author not found'}


def test_get_books(app):
    author_id = create_author("Stephen Hawking")
    create_book(author_id, "Short story of universe")
    create_book(author_id, "Short story of universe")

    response = requests.get("http://127.0.0.1:8000/v1/books")
    assert response.status_code == 200
    assert response.json() == {
        "books": [
            {"id": 1, "title": "Short story of universe",
                "author": "Stephen Hawking"},
            {"id": 2, "title": "Short story of universe", "author": "Stephen Hawking"}
        ]
    }


def test_get_book(app):
    author_id = create_author("Stephen Hawking")
    create_book(author_id, "Short story of universe")

    response = requests.get("http://127.0.0.1:8000/v1/books/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1, "title": "Short story of universe", "author": "Stephen Hawking"}

    response = requests.get("http://127.0.0.1:8000/v1/books/2")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Book not found'}
