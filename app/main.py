from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import router as api_v1_router
from app.api.oauth import router as oauth_router
from app.api.login import router as login_router

app = FastAPI()

app.include_router(login_router)
app.include_router(api_v1_router)
app.include_router(oauth_router)

app.mount("/ui", StaticFiles(directory="app/ui", html=True), name="ui")
