"""User CRUD operations."""

from fastcrud import FastCRUD

from app.models.user import User
from app.schemas.user import UserCreate

# Create CRUD instance
user_crud = FastCRUD(User)
