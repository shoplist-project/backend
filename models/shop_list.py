import uuid
from datetime import datetime
from models import db
from enum import IntEnum


class Access(IntEnum):
    Read = 1
    Write = 2


class ShopList(db.Model):
    __tablename__ = "shop_lists"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    owner = db.relationship("User", backref=db.backref("owned_shop_lists", lazy=True))
    products = db.relationship(
        "Product", backref="shop_list", lazy=True, cascade="all, delete-orphan"
    )
    shared_with = db.relationship(
        "ShopListShare", backref="shop_list", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "access": Access.Write,
            "ownerId": self.owner_id,
            "sharedWith": [share.to_dict() for share in self.shared_with],
            "products": [product.to_dict() for product in self.products],
        }


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    strikeout = db.Column(db.Boolean, default=False)
    shop_list_id = db.Column(
        db.String(36), db.ForeignKey("shop_lists.id"), nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {"id": self.id, "name": self.name, "strikeout": self.strikeout}


class ShopListShare(db.Model):
    __tablename__ = "shop_list_shares"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    shop_list_id = db.Column(
        db.String(36), db.ForeignKey("shop_lists.id"), nullable=False
    )
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    access = db.Column(db.Integer, default=Access.Read.value, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = db.relationship("User", backref=db.backref("shared_shop_lists", lazy=True))

    def to_dict(self):
        return {"username": self.user.username, "access": Access(self.access)}
