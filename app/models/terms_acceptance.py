from app.models.base import Base, db

class TermsAcceptance(Base):
    __tablename__ = 'terms_acceptance'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    version = db.Column(db.String(20), unique=True, nullable=False)
    terms_id = db.Column(db.Integer, db.ForeignKey('terms_and_conditions.id'), nullable=False)
    ip = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
