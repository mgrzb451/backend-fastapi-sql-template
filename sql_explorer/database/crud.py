from .schemas import Note
from sqlalchemy import select
from fastapi import HTTPException


class Crud:
  '''These function will be called in the path operation functions. There we will use dependency injection to pass a context managed database session to the db_session parameter'''

  @staticmethod
  async def get_all_notes(db_session):
    statement = select(Note).order_by(Note.id)
    result = await db_session.execute(statement)
    # Convert the raw data pulled from the SQL table into a format that Pydantic model can parse to then create a new Note object to send in the response
    # we have to convert to an iterator using .scalar().all()
    return result.scalars().all()
  
  @staticmethod
  async def add_new_note(db_session, new_note:Note):
    db_session.add(new_note)
    # Send all pending operations to the db. This will generate the timestamp we specified in the default argument in the Note schema
    await db_session.flush()
    # This will find our newly created note in the temporary view of the database and retrieve it for us with all the defaults (timestamp) and the assigned ID
    await db_session.refresh(new_note)
    # Now we finally commit the new note to the database for real
    # When adding, deleting or updating records (basically changing the data in the table) we have to call .commit()
    await db_session.commit()
    return f"New note {new_note.title} with id {new_note.id} created at {new_note.date_created}"

  @staticmethod
  async def _get_note_by_id_helper(db_session, note_id:int):
    # We need to find a note by id in several methods so we implement a private callback function to handle the retrieval and potential error.
    # We use the dedicated .get() method for retrieving items by their primary key
    note = await db_session.get(Note, note_id)
    if not note:
      raise HTTPException(status_code=404, detail=f"Note with id: {note_id} not found")
    return note

  async def get_note(self, db_session, note_id):
    """Public method for single note retrieval utilizing the private _get_note_by_id_helper()"""
    return await self._get_note_by_id_helper(db_session=db_session, note_id=note_id)

  async def update_note(self, db_session, note_id, updated_note_data):
    note = await self._get_note_by_id_helper(db_session=db_session, note_id=note_id)
    note.title = updated_note_data.title
    note.content = updated_note_data.content
    await db_session.commit()
    return f"Note {note.title} updated"
  
  async def delete_note(self, db_session, note_id):
    # retrieve the node
    note = await self._get_note_by_id_helper(db_session=db_session, note_id=note_id)
    # delete the note
    # IMPORTANT: all session methods have to be awaited to take effect!
    await db_session.delete(note)
    # update the database
    await db_session.commit()
    return f"Note {note.title} with id {note.id} removed"



class CrudOld:

  # These function will be called in the path operation functions. There we will use dependency injection to pass a context managed database session to the db_session_local parameter
  async def dependency_injected_get_all_notes(self, db_session_local):
    statement = select(Note).order_by(Note.id)
    result = await db_session_local.execute(statement)
    # Convert the raw data pulled from the SQL table into a format that Pydantic model can parse to then create a new Note object to send in the response
    return result.scalars().all()
    
  async def dependency_injected_add_new_note(self, db_session_local, new_note:Note):
    db_session_local.add(new_note)


  # I think that using an all-size-fits all dependency to establish local session that commits regardless of necessity and prevents us from ex. refreshing the DB at various points or performing multiple updates within one CRUD function is worse.
  # I think it's better to create a local session using `with db_session() as session:` in each CRUD function and then manually commit() at the end if needed. Yes, there is code repetition but we get better performance and we can control what happens to the database and when
  @staticmethod
  async def get_all_notes(db_session):
    async with db_session() as session:
      statement = select(Note).order_by(Note.id)
      result = await session.execute(statement)
      # we have to convert to an iterator using .scalar().all()
      return result.scalars().all()
    
  @staticmethod
  async def _get_note_by_id_helper(session, note_id:int):
    # We need to find a note by id in several methods so we implement a private callback function to handle the retrieval and potential error using the session of the calling function. This way we don't have to start and stop multiple sessions as in the update_note_with_method_reuse()
    '''
    Retrieve a note with a matching ID from the database using a session from the higher order function
    '''
    note = await session.get(Note, note_id)
    if not note:
      raise HTTPException(status_code=404, detail="Note with id: {note_id} not found")
    return note
  
  async def get_note(self, db_session, note_id):
    """Public method for standalone note retrieval utilizing the private _get_note_by_id_helper()"""
    async with db_session() as session:
      return await self._get_note_by_id_helper(session=session, note_id=note_id)

  async def get_note_old(self, db_session, note_id):    
    async with db_session() as session:
      # We use .get() method which is optimized for finding items by their primary key
      result = await session.get(Note, note_id)
      if not result:
          raise HTTPException(status_code=404, detail="Note with id: {note_id} not found")
      return result
      # If we wanted to find an item by a different attribute we'd use where() like this:
      '''
      # This time we convert to scalars() and then use .first() to get a single value rather than a list or whatever .all() returns
      statement = select(Note).where(Note.id == note_id)
      result = await session.execute(statement)
      note = result.scalars().first()
      '''
     
  @staticmethod
  async def add_new_note(db_session, new_note:Note):
    async with db_session() as session:
        session.add(new_note)
        # Do all pending operations to the db. This will generate the timestamp we specified in the default argument in the Note schema
        await session.flush()
        # This will find our newly created note in the temporary view of the database and retrieve it for us with all the defaults (timestamp) and the assigned ID
        await session.refresh(new_note)
        # Now we finally commit the new note to the database for real
        # When adding, deleting or updating records (basically changing the data in the table) we have to call .commit()
        await session.commit()
        return f"New note {new_note.title} with id {new_note.id} created at {new_note.date_created}"
      
  async def update_note_with_method_reuse(self, db_session, note_id, updated_note_data):
    # we want to reuse the get_note_old() method we already have. That method calls db_session in its own with context manager so we pass just the db_session instance to it (without parenthesis) outside of a context manager so it can do its thing
    note = await self.get_note_old(db_session=db_session, note_id=note_id)
    # we got the note from database and the session opened by get_note_old was closed
    # now we modify the note that was returned by get_note_old()
    note.title = updated_note_data.title
    note.content = updated_note_data.content

    # now we're gonna save it to the db. We open a new session cause the previous one was closed
    async with db_session() as session:
      # we call .merge() to carry over the changes made into this session
      await session.merge(note)
      # and we commit
      await session.commit()
    # NOTE: This approach sucks cause we're opening and closing, opening and closing a session. Better approach is to use the _get_note_by_id_helper()
    return f"Note {note.title} updated"
  

  async def update_note(self, db_session, note_id, updated_note_data):
    async with db_session() as session:
      note = await self._get_note_by_id_helper(session=session, note_id=note_id)
      note.title = updated_note_data.title
      note.content = updated_note_data.content
      await session.commit()
    return f"Note {note.title} updated"


  async def delete_note(self, db_session, note_id):
    async with db_session() as session:
      # retrieve the node
      note = await self._get_note_by_id_helper(session=session, note_id=note_id)
      # delete the note
      # IMPORTANT: all session methods have to be awaited to take effect!
      await session.delete(note)
      # update the database
      await session.commit()
    return f"Note {note.title} with id {note.id} removed"
  
'''
THIS IS THE CORRECT WAY TO IMPLEMENT DEPENDENCY INJECTION FOR NEXT PROJECT

async def establish_session_to_db():
  # This will borrow a connection from the pool and yield a session object that will last until the path operation function returns. This way we don't need to retype "async with db_session() as session:" in every CRUD function 
  async with db_session() as session:
    yield session

@app.patch("/update/item_id")
async def update_item(db = Depends(establish_session_to_db), item_id, new_item_title):
  # establish_session_to_db() yields a session object called db
  # I perform the update
  item = await db.get(Item, item_id)
  if not item:
    raise HTTPException(status_code=404)
  item.title = new_item_title
  # Commit the changes to the session
  await db.commit()
  return
  # Context manager in the establish_session_to_db() dependency closes the session and return to pool
'''

'''
async def establish_session_to_db():
  async with db_session() as session:
    yield session

async def get_item_by_id_helper(session, item_id):
  item = await session.get(Item, item_id)
  if not item:
    raise HTTPException(status_code=404)
  return item

@app.patch("/update/{item_id}")
async def update_item(db = Depends(establish_session_to_db), item_id, new_item_title):
  # sessions to database started
  item = await get_item_by_id_helper(session=db, item_id=item_id)
  # session to database returned 
  # the code below will not have a session to the database?
  item.title = new_item_title
  await db.commit()
  return
'''