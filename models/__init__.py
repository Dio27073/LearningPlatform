from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .models import Role, User, Quiz, Flashcard, FlashcardSet
