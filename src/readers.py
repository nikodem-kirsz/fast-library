import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from . import db


log = logging.getLogger(__name__)
router = APIRouter()


async def get_reader_from_db(reader_id: int):
    query = """
        SELECT
            readers.id,
            readers.name
        FROM 
            readers
        WHERE
            readers.id = ?
    """
    cursor = await db.connection.execute(query, (reader_id,))
    return await cursor.fetchone()


class Reader(BaseModel):
    name: str


@router.post("/v1/readers", status_code=201)
async def add_reader(reader: Reader):
    reader_id = (await db.connection.execute_insert(
        """
        INSERT INTO readers
            (name)
        VALUES (?)
        """,
        (reader.name,),
    ))[0]
    log.debug(f"Reader added {reader.name}")
    return {"reader_id": reader_id}


@router.get("/v1/readers/{reader_id}")
async def get_reader(reader_id: int):
    row = await get_reader_from_db(reader_id)
    if row:
        reader_id, reader_name = row
        return {"id": reader_id, "name": reader_name}
    else:
        raise HTTPException(status_code=404, detail="Reader not found")


@router.get("/v1/readers")
async def get_readers():
    async with db.connection.execute(
        """
        SELECT
            id,
            name
        FROM
            readers
        """
    ) as cursor:
        rows = await cursor.fetchall()

    return {"readers": [{"id": item[0], "name": item[1]} for item in rows]}
