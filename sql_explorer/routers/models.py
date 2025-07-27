# These are response models for our API to send over

from pydantic import BaseModel, ConfigDict
from datetime import datetime

class NoteIn(BaseModel):
  # This is what we expect to come in the request for creating a new note
  title: str
  content: str

  # in model_config we can specify json_schema_extra dict with examples of valid requests etc. for the API docs
  # model_config = ConfigDict(
  #   from_attributes=True
  # )

class NoteOut(NoteIn):
  # This is what we'll add to attributes specified in NoteIN. We will send all 4 of these in the response body when sending notes to the user or when sending Notes to our database handlers
  id: int
  date_created: datetime

'''Important to add that this not only validates the data coming in and out but also parses the data and we can decide what gets read. E.g. If the request contains title, content and description, since we didn't specify description field in the NoteIn it will be ignored and not read'''