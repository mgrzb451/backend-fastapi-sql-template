import uvicorn

if __name__ == "__main__":
  uvicorn.run(app="sql_explorer.sql_api:app", reload=True)