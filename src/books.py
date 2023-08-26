import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from . import authors

from . import db


log = logging.getLogger(__name__)
router = APIRouter()

async def get_book_from_db(book_id: int):
    query = """
        SELECT
            books.id,
            books.title,
            authors.name
        FROM 
            books
        JOIN
            authors ON authors.id = books.author_id
        WHERE
            books.id = ?
    """
    cursor = await db.connection.execute(query, (book_id,))
    return await cursor.fetchone()

class Book(BaseModel):
    author_id: int
    title: str


@router.post("/v1/books", status_code=201)
async def add_book(book: Book):
    author = await authors.get_author_from_db(book.author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    book_id = (await db.connection.execute_insert(
        """
        INSERT INTO books
            (author_id, title)
        VALUES (?, ?)
        """,
        (book.author_id, book.title),
    ))[0]

    log.debug(f"Book added {book.title}")

    return {"book_id": book_id}

@router.get("/v1/books/{book_id}")
async def get_book(book_id: int):
    row = await get_book_from_db(book_id)
    if row:
        book_id, title, author_name = row
        return {"id": book_id, "title": title, "author": author_name}
    else:
        raise HTTPException(status_code=404, detail="Book not found")
    
@router.get("/v1/books")
async def get_books():
    async with db.connection.execute(
        """
        SELECT
            books.id,
            books.title,
            authors.name
        FROM
            books
        JOIN
            authors ON authors.id = books.author_id
        """
    ) as cursor:
        rows = await cursor.fetchall()

    return {"books": [{"id": item[0], "title": item[1], "author": item[2]} for item in rows]}
