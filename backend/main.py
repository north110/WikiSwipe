from fastapi import FastAPI, Depends, HTTPException, status
from .database import engine, Base, SessionLocal
from . import models
import requests
from typing import List
from fastapi import FastAPI, Body, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .models import UserInteraction
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from fastapi import Response
from fastapi.middleware.cors import CORSMiddleware


SECRET_KEY = "CHANGE_THIS_TO_A_SECRET_KEY"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

templates = Jinja2Templates(directory="templates")

# Create all tables defined in models if they don't already exist
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

@app.get("/login_page")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/")
def home(request: Request):
    # The front-end will check localStorage for the token.
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/signup")
def signup(user_data: dict = Body(...), db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user_data["email"]).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user_data["password"])
    new_user = models.User(
        username=user_data["username"],
        email=user_data["email"],
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    token_data = {"sub": user.id}
    token = create_access_token(token_data)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/like_article")
def like_article(
    article_id: int = Body(...),
    user_id: int = Body(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interaction = UserInteraction(
        user_id=user_id,
        article_id=article_id,
        interaction_type='like'
    )
    db.add(interaction)
    db.commit()
    return {"message": "Article liked!"}


# @app.post("/search_wikipedia")
# def search_wikipedia(
#     keywords: List[str],
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     search_results = {}
#     for keyword in keywords:
#         response = requests.get(
#             f"https://en.wikipedia.org/w/api.php?action=opensearch&search={keyword}&limit=5&format=json"
#         )
#         if response.status_code == 200:
#             data = response.json()
#             search_results[keyword] = data[1]
#         else:
#             search_results[keyword] = []
#     return {"results": search_results}

