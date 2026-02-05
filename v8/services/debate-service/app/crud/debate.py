from fastcrud import FastCRUD
from app.models.debate import Debate
from app.schemas.debate import DebateCreate


debate_crud = FastCRUD(Debate)
