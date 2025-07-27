from fastapi import FastAPI
from sql_explorer.routers import notes_router
from contextlib import asynccontextmanager
from sql_explorer.database.db import engine, init_db


# We use this function in conjunction with lifespan parameter in app=FastAPI to define what actions should happen at the start of our app and when it's closed
# This can also be used to ex. start generating content with an LLM or some other long lasting task
@asynccontextmanager
async def life_span(app:FastAPI):
  """yield separates startup logic (before yield) from shutdown logic (after yield)"""
  # All code until yield will happen at app startup
  print("--Server starting--")
  await init_db() # Tables created, connection returned to pool
  yield # App runs - pool is STILL OPEN and available
  # All code after yield will happen when the app termination starts
  print("--Server shutdown--")
  # Close the connection to the database when the app terminates
  await engine.dispose() # Pool closed during shutdown
  

description = """## Purpose
To learn the correct way of setting up a proper project structure based on many disparate sources
 * using asynchronous path operations
 * creating an asynchronous **SQLAlchemy database** and using it *asynchronously*

## This is Markdown
How cool is that!
"""
# lifespan=life_span we pass the life_span function that creates database tables if needed and establishes a connection pool for local session that perform CRUD
app=FastAPI(title="FastAPI with SQLAlchemy:sqlite Learning Project", description=description, lifespan=life_span)

@app.get("/")
async def home()->str:
  '''
  # Welcome to the Homepage
  ## This is a path operation added directly to the app despite the rest being added through a **router**
  '''
  return "Hello!"

# add the router to the main API app
app.include_router(notes_router)