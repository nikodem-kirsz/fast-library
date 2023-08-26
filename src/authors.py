import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from . import db


log = logging.getLogger(__name__)
router = APIRouter()


class Author(BaseModel):
    name: str

async def get_author_from_db(author_id: int):
    query = """
        SELECT
            authors.id,
            authors.name
        FROM 
            authors
        WHERE
            authors.id = ?
    """
    cursor = await db.connection.execute(query, (author_id,))
    return await cursor.fetchone()

@router.post("/v1/authors", status_code=201)
async def add_author(author: Author):
    author_id = (await db.connection.execute_insert(
        """
        INSERT INTO authors (name) VALUES (?)
        """,
        (author.name,),
    ))[0]
    log.debug(f"Author added {author.name}")

    return {"author_id": author_id}

@router.get("/v1/authors/{author_id}")
async def get_author(author_id: int):
    row = await get_author_from_db(author_id)
    if row:
        author_id, author_name = row
        return {"id": author_id, "title": author_name}
    else:
        raise HTTPException(status_code=404, detail="Author not found")

@router.get("/v1/authors")
async def get_authors():
    async with db.connection.execute(
        """
        SELECT
            id, name
        FROM
            authors
        ORDER BY id ASC
        """
    ) as cursor:
        rows = await cursor.fetchall()

    return {"authors": [{"id": item[0], "name": item[1]} for item in rows]}
