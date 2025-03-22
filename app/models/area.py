from app.models.base import Base, db

class Area(Base):
    __tablename__ = "areas"
    area_name = db.Column(db.String(50), nullable=False)
    number_of_trees_planted = db.Column(db.Integer, nullable=False)
    planting_techniques = db.Column(db.String(50), nullable=False)
    total_area_hectares = db.Column(db.Float, nullable=False)
    reflorested_area_hectares = db.Column(db.Float, nullable=False)
    planted_species = db.Column(db.String(50), nullable=False)
    initial_planted_area_hectares = db.Column(db.Float, nullable=False)
    initial_vegetation_cover = db.Column(db.String(50), nullable=False)

    localization_id = db.Column(
        db.Integer, db.ForeignKey("localizations.id"), nullable=False
    )
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
