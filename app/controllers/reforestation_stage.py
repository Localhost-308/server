from flask import Blueprint, abort, request, jsonify
from flask_jwt_extended import jwt_required
from collections import Counter

from app.initializer import app, mongo
from app.database import db
from app.models import Area, Localization 
from app.schemas import AreaSchema


reforestation = Blueprint("reforestation", __name__, url_prefix=app.config["API_URL_PREFIX"] + "/reforestation")

def get_area_ids_by_uf(uf):
    areas = db.session.query(Area.id).join(Localization).filter(Localization.uf == uf).with_entities(Area.id).all()
    return [area.id for area in areas]


def get_stage_counts(area_ids):
    if not area_ids:
        return {}
    areas_data = mongo.db.reforestation_stages.find({"area_id": {"$in": area_ids}})
    stage_counts = Counter(area["stage_indicator"] for area in areas_data)
    return stage_counts

@reforestation.route("/stages", methods=["GET"])
@jwt_required()
def get_reforestation_stages():
    uf = request.args.get("uf", "").strip().upper()

    if not uf:
        return jsonify({"error": "UF é obrigatória!"}), 400
    
    area_ids = get_area_ids_by_uf(uf)

    if not area_ids:
        return jsonify({"error": "Nenhuma área encontrada para esta UF."}), 404

    stage_counts = get_stage_counts(area_ids)

    if not stage_counts:
        return jsonify({"error": "Nenhum estágio encontrado para as áreas da UF."}), 404

    return jsonify({"uf": uf, "stage_counts": stage_counts})
