import requests

from helpers import create_author, create_book, create_borrow, create_reader


def test_add_borrows_success(app):
    author_id = create_author("Stephen Hawking")

    book_response = create_book(author_id, "Short story of universe")
    assert book_response.status_code == 201
    assert book_response.ok
    book_json = book_response.json()
    assert "book_id" in book_json

    reader_id = create_reader("Nikodem")

    response = create_borrow(reader_id, book_json["book_id"])

    assert response.status_code == 201
    assert response.ok
    assert response.json() == {'borrow_id': 1}


def test_add_borrows_success_when_same_user_borrows(app):
    author_id = create_author("Stephen Hawking")

    book_response = create_book(author_id, "Short story of universe")
    assert book_response.status_code == 201
    assert book_response.ok
    book_json = book_response.json()
    assert "book_id" in book_json

    reader_id = create_reader("Nikodem")

    response = create_borrow(reader_id, book_json["book_id"])
    response = create_borrow(reader_id, book_json["book_id"])

    assert response.status_code == 201
    assert response.ok
    assert response.json() == {'borrow_id': 1}


def test_add_borrows_failure_when_book_already_borrowed(app):
    author_id = create_author("Stephen Hawking")

    book_response = create_book(author_id, "Short story of universe")
    assert book_response.status_code == 201
    assert book_response.ok
    book_json = book_response.json()
    assert "book_id" in book_json

    reader_id__1 = create_reader("Nikodem")
    reader_id__2 = create_reader("Marta")

    create_borrow(reader_id__1, book_json["book_id"])
    response = create_borrow(reader_id__2, book_json["book_id"])

    assert response.status_code == 403
    assert response.json() == {
        'detail': 'Book is already borrowed by someone else'}


def test_add_borrows_failure_non_existing_book(app):
    reader_id = create_reader("Nikodem")

    response = create_borrow(reader_id, 1)

    assert response.status_code == 404
    assert response.json() == {'detail': 'Book not found'}


def test_add_borrows_failure_non_existing_reader(app):
    author_id = create_author("Stephen Hawking")

    book_response = create_book(author_id, "Short story of universe")
    assert book_response.status_code == 201
    assert book_response.ok
    book_json = book_response.json()
    assert "book_id" in book_json

    response = create_borrow(1, book_json["book_id"])

    assert response.status_code == 404
    assert response.json() == {'detail': 'Reader not found'}
