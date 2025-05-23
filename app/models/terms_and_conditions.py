from app.models.base import Base, db

class TermsAndCondition(Base):
    __tablename__ = 'terms_and_conditions'
    version = db.Column(db.String(20), unique=True, nullable=False)
    text = db.Column(db.Text, nullable=False)
    mandatory = db.Column(db.Boolean, default=True)
