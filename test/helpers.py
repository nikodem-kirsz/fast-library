import requests

def create_author(author_name):
    response = requests.post("http://127.0.0.1:8000/v1/authors", json={"name": author_name})
    assert response.status_code == 201
    assert response.ok
    response_json = response.json()
    assert "author_id" in response_json
    return response_json["author_id"]

def create_book(author_id, title):
    return requests.post("http://127.0.0.1:8000/v1/books", json={"author_id": str(author_id), "title": title})

def create_reader(name):
    response = requests.post("http://127.0.0.1:8000/v1/readers", json={"name": name})
    assert response.status_code == 201
    assert response.ok
    response_json = response.json()
    assert "reader_id" in response_json
    return response_json["reader_id"]

def create_borrow(reader_id, book_id):
    return requests.post("http://127.0.0.1:8000/v1/borrows", json={"reader_id": str(reader_id), "book_id": str(book_id)})
    