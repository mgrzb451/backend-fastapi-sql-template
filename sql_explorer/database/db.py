# For loading environment variables
import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import asyncio
from .schemas import Base

# Load the Database name string from the .env file located in the project root directory using python-dotenv package (installed by default with FastAPI)
load_dotenv() # this loads all the env variables saved in the .env file and makes them available for os.getenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# check_same_thread=False is necessary only for async sqlite (omit with postgresql)
# Recent aiosqlite versions set check_same_thread=False internally. setting check_same_thread=False in recent versions of aiosqlite causes an error. Don't include it
"""engine is a Connection Pool Manager
it creates a persistent connection pool, not a single connection.
This pool stays open until explicitly disposed. Sessions we create later with async_sessionmaker borrow connections from the pool temporarily for CRUD"""
engine = create_async_engine(
  url=DATABASE_URL,
  # check_same_thread=False,
  echo=True # to see queries in the terminal output
)

async def init_db():
  """temporarily borrows one connection from the pool created by create_async_engine() The connection is automatically returned to the pool when the context exits."""
  # Context Managers Manage Individual Connections
  async with engine.begin() as conn:
    # create_all has an built-in check to know if tables already exist and won't modify or overwrite them when called. It's safe to use on every app startup
    await conn.run_sync(Base.metadata.create_all)
    print("Database initialized")

# creates an object for handling temporary connections to reach into the database (for when we want to run CRUD operations)
# expire_on_commit=False means the session won't expire immediately after we db.commit() something to the database. So we can ex. access the data we just inserter into db without starting a new session just to retrieve it within one path operation
# autoflush=False makes it so pending changes aren't automatically committed to the db, only when we call .commit() -> better performance, safer etc.
db_session = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

# This is only for manual DB reset
async def reset_db():
  '''
  **DANGER** _Reset_ Tables inside our database
  '''
  async with engine.begin() as conn:
    # run_sync() allows traditional synchronous SQLAlchemy functions to run within with asyncio
    # DANGER: drop_all() method removes the existing data tables and all the stored data
    await conn.run_sync(Base.metadata.drop_all)
    # create_all() has an built-in check to know if tables already exist and won't modify or overwrite them when called. It's safe to use on every app startup
    await conn.run_sync(Base.metadata.create_all)

  # This is only advisable after the `with`` context manager (not within it) to ensure some in-depth garbage collection stuff...
  await engine.dispose()


if __name__ == "__main__":
  # Running this will 1st remove all data inside DB and then create new empty tables. I guess we're supposed to do it once manually and then when we want to reset the db?
  # I called it with "python -m sql_explorer.database.db" and it seems to have worked. Cool 👍🏻
  print(f"running cause {__name__=}")
  asyncio.run(reset_db())
