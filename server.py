from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from settings import Settings
from db import db_init, full_url_to_short_url, short_url_to_full_url
from os import environ

Settings.base_url = environ.get('BASE_URL', 'http://localhost:8000')
Settings.db_file_path = environ.get('DB_FILE_PATH', '/app/db/db.sqlite3')
Settings.db_lock_file_path = environ.get('DB_LOCK_FILE_PATH', f'{Settings.db_file_path}.lock')

app = FastAPI()
db_init()


class ShortenRequest(BaseModel):
    url: str


@app.post("/url/shorten")
async def url_shorten(request: ShortenRequest):
    """
    Given a URL, generate a short version of the URL that can be later resolved to the originally
    specified URL.
    """

    short_url = full_url_to_short_url(request.url)

    return {"short_url": f"{Settings.base_url}/r/{short_url}"}


# I don't see the point of this when we only return a redirect or 404...
# class ResolveRequest(BaseModel):
#     short_url: str


@app.get("/r/{short_url}")
async def url_resolve(short_url: str):
    """
    Return a redirect response for a valid shortened URL string.
    If the short URL is unknown, return an HTTP 404 response.
    """

    full_url = short_url_to_full_url(short_url)

    return RedirectResponse(full_url)


@app.get("/")
async def index():
    return "Your URL Shortener is running!"
