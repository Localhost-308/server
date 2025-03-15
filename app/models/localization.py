from app.models.base import Base, db


class Localization(Base):
    __tablename__ = "localizations"
    uf = db.Column(db.String(2), nullable=False)
    city = db.Column(db.String(2), nullable=False)
    altitude = db.Column(db.Float, nullable=False)
    soil_type = db.Column(db.String(50), nullable=False)
