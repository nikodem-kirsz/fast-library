import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from . import books
from . import readers

from . import db


log = logging.getLogger(__name__)
router = APIRouter()


async def get_borrow_from_db(book_id: int):
    cursor = await db.connection.execute(
        """
        SELECT
            borrows.id,
            borrows.borrow_time,
            readers.id,
            readers.name,
            books.title,
            authors.name
        FROM
            borrows
        LEFT JOIN
            books ON books.id = borrows.book_id  
        LEFT JOIN
            authors ON authors.id = books.author_id
        LEFT JOIN
            readers ON readers.id = borrows.reader_id 
        WHERE
            borrows.book_id = ?         
        """,
        (book_id,),
    )
    return await cursor.fetchone()


class Borrow(BaseModel):
    reader_id: int
    book_id: int


@router.post("/v1/borrows", status_code=201)
async def add_borrow(borrow: Borrow):
    reader = await readers.get_reader_from_db(borrow.reader_id)
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    book = await books.get_book_from_db(borrow.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    borrows = await get_borrow_from_db(borrow.book_id)
    if borrows:
        borrows_id, _, readers_id, _, _, _ = borrows
        if readers_id != borrow.reader_id:
            raise HTTPException(
                status_code=403, detail="Book is already borrowed by someone else")
        else:
            return {"borrow_id": borrows_id}

    borrow_id = (await db.connection.execute_insert(
        """
        INSERT INTO borrows
            (reader_id, book_id, borrow_time, return_time)
        VALUES
            (?, ?, DATE('now'), NULL)
        """,
        (borrow.reader_id, borrow.book_id),
    ))[0]
    log.debug(f"New borrow from reader id {borrow.reader_id}")
    return {"borrow_id": borrow_id}


@router.delete("/v1/borrows/{book_id}")
async def del_borrow(book_id: int):
    await db.connection.execute(
        """
        UPDATE
            borrows
        SET
            return_time = DATE('now')
        WHERE
            book_id = ?
            AND return_time IS NULL;
        """,
        (book_id,),
    )
    log.debug(f"Book {book_id} returned.")


@router.get("/v1/borrows/{book_id}")
async def get_borrow(book_id: int):
    row = await get_borrow_from_db(book_id)
    if row:
        borrows_id, readers_name, readers_id, title, author_name, borrow_time = row
        return {
            "id": borrows_id,
            "borrow_time": borrow_time,
            "readers_id": readers_id,
            "readers_name": readers_name,
            "title": title,
            "author": author_name
        }


@router.get("/v1/borrows")
async def get_borrows():
    async with db.connection.execute(
        """
        SELECT
            readers.name,
            books.title,
            authors.name,
            borrows.borrow_time
        FROM
            borrows
        LEFT JOIN
            books ON books.id = borrows.book_id
        LEFT JOIN
            authors ON authors.id = books.author_id
        LEFT JOIN
            readers ON readers.id = borrows.reader_id
        WHERE
            borrows.return_time IS NULL
        """
    ) as cursor:
        rows = await cursor.fetchall()

    return {
        "borrows": [{"reader": item[0], "title": item[1], "author": item[2], "borrow_time": item[3]} for item in rows]
    }
