# app/main.py
from fastapi import FastAPI, APIRouter
from .routers import formations

version = APIRouter(prefix="/v1")
# /v1/formations
version.include_router(formations.router)

app = FastAPI(title="API Catalogue", version="1.0.0")


@app.get("/v1/health")
def healthcheck() -> dict[str, str]:
    return {"statut": "ok"}

# domain/v1/...
app.include_router(version)