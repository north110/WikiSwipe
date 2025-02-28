from fastapi import FastAPI
from .database import engine, Base
from . import models
import requests
from typing import List
from fastapi import FastAPI, Body, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import UserInteraction

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app = FastAPI()

# Create all tables defined in models if they don't already exist
Base.metadata.create_all(bind=engine)
@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



@app.post("/search_wikipedia")
def search_wikipedia(keywords: List[str]):
    search_results = {}
    for keyword in keywords:
        response = requests.get(
            f"https://en.wikipedia.org/w/api.php?action=opensearch&search={keyword}&limit=5&format=json"
        )
        if response.status_code == 200:
            data = response.json()
            # data[1] usually contains the search result titles
            search_results[keyword] = data[1]
        else:
            search_results[keyword] = []
    return {"results": search_results}


@app.post("/like_article")
def like_article(article_id: int = Body(...), user_id: int = Body(...)):
    db: Session = SessionLocal()
    interaction = UserInteraction(
        user_id=user_id,
        article_id=article_id,
        interaction_type='like'
    )
    db.add(interaction)
    db.commit()
    db.close()
    return {"message": "Article liked!"}
