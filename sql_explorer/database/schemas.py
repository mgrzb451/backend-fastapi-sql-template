#  These are schemas defining our data structure for the SQL Tables

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, func
from datetime import datetime


class Base(DeclarativeBase):
  pass

class Note(Base):
  # Name of the table storing Note element data
  __tablename__ = "notes"

  id: Mapped[int] = mapped_column(primary_key=True)
  title: Mapped[str] = mapped_column(String(50), nullable=False)
  content: Mapped[str] = mapped_column(Text, nullable=False)
  # we are passing sqlalchemy func.now() to the default parameter to generate a datetime object at the moment of Note record creation
  date_created: Mapped[datetime] = mapped_column(default=func.now())
  # INFO: if we wanted to use a different function ex. datetime.now() or our own custom function we have to pass a reference (no parenthesis) NOT call it. Otherwise it will return the time the application starts for every single note 😑 e.g.:
  # date_created: Mapped[datetime] = mapped_column(default=datetime.now)