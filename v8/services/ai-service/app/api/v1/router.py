from fastapi import APIRouter

from app.api.v1 import agents, analyze, judge

api_router = APIRouter()

api_router.include_router(analyze.router)
api_router.include_router(judge.router)
api_router.include_router(agents.router)
