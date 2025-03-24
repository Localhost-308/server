from flask import Blueprint, abort, request, jsonify
from flask_jwt_extended import jwt_required
from collections import Counter
from flasgger import swag_from

from app.initializer import app, mongo
from app.database import db
from app.models import Area, Localization 
from app.schemas import AreaSchema


reforestation = Blueprint(
    "reforestation", __name__, url_prefix=app.config["API_URL_PREFIX"] + "/reforestation"
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


def get_stage_counts(area_names):
    if not area_names:
        return {}
    areas_data = mongo.db.api.find({"area_name": {"$in": area_names}})
    stage_counts = Counter(area["stage_indicator"] for area in areas_data)
    return stage_counts

@reforestation.route("/stages", methods=["GET"])
#@jwt_required()
@swag_from({
    'tags': ['Reforestation'],
    'summary': 'Get the reforestation stages by UF',
    'description': 'Retrieve the count of areas in different stages of reforestation based on the UF provided.',
    'parameters': [
        {
            'name': 'uf',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'The UF (state) to filter the areas by.'
        }
    ],
    'responses': {
        200: {
            'description': 'The reforestation stages and their counts successfully retrieved.',
            'schema': {
                'type': 'object',
                'properties': {
                    'uf': {'type': 'string', 'example': 'RJ'},
                    'stage_counts': {
                        'type': 'object',
                        'properties': {
                            'Em progresso': {'type': 'integer', 'example': 864},
                            'Em recuperação': {'type': 'integer', 'example': 1625},
                            'Estabilizado': {'type': 'integer', 'example': 1649},
                            'Iniciado': {'type': 'integer', 'example': 1060},
                            'Área Reflorestada': {'type': 'integer', 'example': 1437}
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Invalid UF parameter provided.',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'UF é obrigatória!'}
                }
            }
        },
        404: {
            'description': 'No data found for the provided UF.',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Nenhuma área encontrada para esta UF.'}
                }
            }
        }
    }
})
def get_reforestation_stages():
    uf = request.args.get("uf", "").strip().upper()


    if not uf:
        return jsonify({"error": "UF é obrigatória!"}), 400
    
    area_names = get_area_names_by_uf(uf)

    if not area_names:
        return jsonify({"error": "Nenhuma área encontrada para esta UF."}), 404

    stage_counts = get_stage_counts(area_names)

    if not stage_counts:
        return jsonify({"error": "Nenhum estágio encontrado para as áreas da UF."}), 404

    return jsonify({"uf": uf, "stage_counts": stage_counts})
