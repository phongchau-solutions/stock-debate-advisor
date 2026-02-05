"""User CRUD operations."""

from fastcrud import FastCRUD

from app.models.user import User

# Create CRUD instance
user_crud = FastCRUD(User)
