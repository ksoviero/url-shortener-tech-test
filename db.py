from sqlite3 import connect
from settings import Settings
from struct import pack, unpack
from base64 import urlsafe_b64decode, urlsafe_b64encode
from fastapi.exceptions import HTTPException
from pathlib import Path
from time import sleep


def db_init():
  """
  Initialize the table if it doesn't already exist.
  """

  # SQLite auto creates DB files, so all we have to do is create the table if
  # it doesn't exist.
  _query('create table if not exists short_urls ( url )')


def _lock():
  """
  Create a lock file to ensure only one instance can access the DB at a time.
  """

  p = Path(Settings.db_lock_file_path)

  while p.exists():
    sleep(0.001)

  p.touch()


def _unlock():
  """
  Remove DB lock file when query is complete.
  """

  p = Path(Settings.db_lock_file_path)

  if p.exists():
    p.unlink()


def _query(query: str, params: list = []):
  """
  Connect to the SQLite DB and return the results of the given query.
  """

  try:
    _lock()
    c = connect(Settings.db_file_path)

    with c:
      cur = c.cursor()
      cur.execute(query, params)

      results = cur.fetchone()

    c.close()

    return results

  finally:
    # Always unlock, even on errors.
    _unlock()


def short_url_to_full_url(short_url: str):
  """
  Given a base64 short url code, e.g. "AAAAAA==" return the full URL.
  """

  try:
    rowid = unpack('!L', urlsafe_b64decode(short_url))

  except Exception as e:
    print(e.__class__, e)
    raise HTTPException(status_code=400, detail='Invalid URL short code')

  q = _query('select url from short_urls where rowid = ?', rowid)

  if q is None:
    raise HTTPException(status_code=404, detail='Unknown URL short code')

  return q[0]


def full_url_to_short_url(full_url: str):
  """
  Given a full url, store it and return the base64 short form of the URL, e.g. "AAAAAA==".
  """

  q = _query('insert into short_urls ( url ) values ( ? ) returning rowid', [full_url])
  rowid = q[0]

  return urlsafe_b64encode(pack('!L', rowid)).decode()
