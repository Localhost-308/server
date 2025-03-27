from flask import Blueprint, abort, request, jsonify
from flask_jwt_extended import jwt_required
from collections import Counter
from flasgger import swag_from

from app.initializer import app, mongo
from app.database import db
from app.models import Area, Localization 

environment_threats = Blueprint(
    "environment_threats", __name__, url_prefix=app.config["API_URL_PREFIX"] + "/threats"
)

def get_area_names_by_uf(uf):
    areas = (db.session
            .query(Area.area_name)
            .join(Localization)
            .filter(Localization.uf == uf)
            .with_entities(Area.area_name)
            .all())
    area_names = []
    for area in areas:
        area_name = area.area_name
        area_uf = area_name.split('-')[1]
        
        if area_uf.upper() == uf: 
            area_names.append(area_name)
    
    return area_names


def get_threat_counts(area_names, threat_type=None):
    if not area_names:
        return {}

    query = {"area_name": {"$in": area_names}}
    if threat_type:
        query["environmental_threats"] = threat_type
    
    areas_data = mongo.db.api.find(query)
    threat_counts = Counter(area["environmental_threats"] for area in areas_data)
    return threat_counts
