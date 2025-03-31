from app.models.base import Base, db


class Company(Base):
    __tablename__ = "companies"
    name = db.Column(db.String(50), nullable=False)
    cnpj = db.Column(db.String(20), nullable=False)
