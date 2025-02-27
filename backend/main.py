from fastapi import FastAPI
from .database import engine, Base
from . import models

app = FastAPI()

# Create all tables defined in models if they don't already exist
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to WikiSwipe API!"}
