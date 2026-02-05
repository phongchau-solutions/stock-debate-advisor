from fastapi import APIRouter
from app.api.v1 import debates

api_router = APIRouter()

api_router.include_router(debates.router)
