import logging

import asyncio
from os import getenv
from fastapi import FastAPI
from uvicorn import Config, Server

from . import authors
from . import books
from . import borrows
from . import db
from . import readers

log = logging.getLogger(__name__)

app = FastAPI()

app.include_router(authors.router)
app.include_router(books.router)
app.include_router(borrows.router)
app.include_router(readers.router)


@app.get("/")
async def root():
    return "Book Library"


@app.on_event("shutdown")
async def app_shutdown():
    if getenv('APP_ENV') == 'APP':
        log.debug("Commiting database commands.")
        await db.connection.commit()
    elif getenv('APP_ENV') == 'TEST':
        log.debug("Test environment. Discarding database commands.")
    log.debug("Closing database connection.")
    await db.connection.close()
    log.debug("Stopping asyncio event loop.")
    asyncio.get_event_loop().stop()


def setup_logging():
    log = logging.getLogger("app")
    if getenv("LOG_LEVEL") == 'DEBUG':
        logging.basicConfig(level=logging.DEBUG)
    log.setLevel(logging.DEBUG)
    logging_handler = logging.StreamHandler()
    logging_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s\t%(levelname)s\t%(message)s")
    logging_handler.setFormatter(formatter)
    log.addHandler(logging_handler)


async def run():
    await db.initialize()
    web_server = Server(Config(app=app, host="0.0.0.0", port=8000))
    await web_server.serve()


if __name__ == "__main__":
    setup_logging()
    loop = asyncio.get_event_loop()
    loop.call_soon(lambda: asyncio.create_task(run()))
    loop.run_forever()
