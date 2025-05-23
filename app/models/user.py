import enum
from app.models.base import Base, db

class CargoEnum(enum.Enum):
    ADMIN = 'ADMIN'
    DONO_AREA = 'DONO_AREA'
    GESTOR_AREA = 'GESTOR_AREA'

class User(Base):
    __tablename__ = 'users'
    first_name = db.Column(db.String(350), nullable=False)
    last_name = db.Column(db.String(350), nullable=False)
    email = db.Column(db.String(350), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False)
    cargo = db.Column(db.Enum(CargoEnum), nullable=False)
    # last_terms_and_conditions_accepted = db.Column(db.Boolean, default=False)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
