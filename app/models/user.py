from app.models.base import Base, db

class User(Base):
    __tablename__ = 'users'
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(162), nullable=False)