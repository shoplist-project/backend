from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import bcrypt
from models import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def set_password(self, password):
        password_bytes = password.encode()
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode()

    def check_password(self, password):
        password_bytes = password.encode()
        hash_bytes = self.password_hash.encode()
        return bcrypt.checkpw(password_bytes, hash_bytes)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
        }
