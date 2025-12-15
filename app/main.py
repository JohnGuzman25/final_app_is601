from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import Base, engine
from app.models import user, transaction

from app.routers.auth import router as auth_router
from app.routers.dashboard import router as dashboard_router
from app.routers.transactions import router as transactions_router

app = FastAPI(title="Final Project – IS601")

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(transactions_router)

@app.get("/health")
def health():
    return {"status": "ok"}

