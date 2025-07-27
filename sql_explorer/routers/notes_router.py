# This is equivalent to Flask's blueprints. It allows us to group path operations (get, post etc.) in separate python modules
from fastapi import APIRouter, HTTPException, Depends
from ..database.crud import Crud
from ..database.db import db_session
from ..database.schemas import Note
from .models import NoteIn, NoteOut

notes_router = APIRouter()

# our API for CRUD operation on the database
crud = Crud()

'''OLD
async def get_db():
  async with db_session() as session:
    try:
      # establish a temporary connection to the database
      # then do whatever CRUD operation
      yield session
      # after the operation commit any changes to the DB
      await session.commit()
    except Exception as error:
      # in case we can't reach the DB or something messes up during CRUD
      await session.rollback()
      raise HTTPException(status_code=500, detail=error)
    finally:
      # at the end close the connection to the DB
      await session.close()
'''

# This is a dependency function that establishes a temporary connection to the database. Waits for changes to the database to happen and afterwards commits the changes and closes the connection. We will use it in path operation function whenever we want to communicate with the database.
# We will use dependency injection via the Depends class that will basically automatically call this function for us and progress it according to the flow of the request/response generation so we don't have to do it manually or retype this functionality every time
async def establish_session_to_db():
  async with db_session() as session:
    yield session

### OPTIMIZED CODE ###
'''Dependency injection spans the entire duration of the path operation function. It will only close the session when the path operation ends. That's why we can use separate functions that reach in and commit to the db multiple times in a single session and it will be fine. The only way the session will close early is if we include a context manager like "async with db_session() as session:" inside one of the CRUD functions. So let's not 😜'''

# tags=[] is the title displayed in the docs used to group different path operations together
@notes_router.get("/notes/", tags=["Viewing Notes"], response_model=list[NoteOut])
async def get_all_notes(db_session_injection = Depends(establish_session_to_db)):
  notes = await crud.get_all_notes(db_session=db_session_injection)
  return notes

# response model in the decorator validates the data sent in the response by our path operations function
# type hint in the function parameters validates the data coming from the frontend - the request
@notes_router.post("/notes/", tags=["Manipulating Notes"], status_code=201, response_model=dict[str, str])
async def create_note(request:NoteIn, db_session_injection = Depends(establish_session_to_db)):
  new_note = Note(
    title=request.title,
    content=request.content
  )
  success_message = await crud.add_new_note(db_session=db_session_injection, new_note=new_note)
  return {"message": success_message}

@notes_router.get("/notes/{note_id}", tags=["Viewing Notes"], response_model=NoteOut)
async def get_note_by_id(note_id: int, db_session_injection = Depends(establish_session_to_db)):
  return await crud.get_note(db_session=db_session_injection, note_id=note_id)

@notes_router.patch("/notes/{note_id}", tags=["Manipulating Notes"], response_model=dict[str, str])
async def update_note(note_id: int, new_note_data: NoteIn, db_session_injection = Depends(establish_session_to_db)):
  success_message = await crud.update_note(db_session=db_session_injection, note_id=note_id, updated_note_data=new_note_data)
  return {"message": success_message}

@notes_router.delete("/notes/{note_id}", tags=["Manipulating Notes"], response_model=dict[str, str])
async def delete_note(note_id: int, db_session_injection = Depends(establish_session_to_db)):
  message = await crud.delete_note(db_session=db_session_injection, note_id=note_id)
  return {"message": message}






'''
### OLD CODE ###

# response model in the decorator validates the data sent in the response by our path operations function
# type hint in the function parameters validates the data coming from the frontend - the request
@notes_router.get("/notes/", tags=["Viewing Notes"], response_model=list[NoteOut])
async def old_get_all_notes():
  notes = await crud.get_all_notes(db_session=db_session)
  return notes

# tags=[] is the title displayed in the docs used to group different path operations together
@notes_router.get("/notes/{note_id}", tags=["Viewing Notes"], response_model=NoteOut)
async def old_get_note_by_id(note_id: int):
  return await crud.get_note(db_session=db_session, note_id=note_id)

@notes_router.post("/notes/", tags=["Manipulating Notes"], status_code=201, response_model=dict[str, str])
async def old_create_note(request:NoteIn):
  new_note = Note(
    title=request.title,
    content=request.content
  )
  success_message = await crud.add_new_note(db_session=db_session, new_note=new_note)
  return {"message": success_message}
  '''

# ⬇ This is an example of a path operation utilizing dependency injection via the Depends Class. I think I prefer using customized context managers defined in each CRUD function
'''@notes_router.post("/notes/", tags=["Manipulating Notes"], status_code=201)
async def create_note(request:NoteIn, db_session_injection = Depends(get_db)):
  new_note = Note(
    title=request.title,
    content=request.content
  )
  await crud.dependency_injected_add_new_note(db_session_local=db_session_injection, new_note=new_note)'''
'''
@notes_router.patch("/notes/{note_id}", tags=["Manipulating Notes"], response_model=dict[str, str])
async def old_update_note(note_id: int, new_note_data: NoteIn):
  success_message = await crud.update_note(db_session=db_session, note_id=note_id, updated_note_data=new_note_data)
  return {"message": success_message}

@notes_router.delete("/notes/{note_id}", tags=["Manipulating Notes"], response_model=dict[str, str])
async def old_delete_note(note_id: int):
  message = await crud.delete_note(db_session=db_session, note_id=note_id)
  return {"message": message}
  '''