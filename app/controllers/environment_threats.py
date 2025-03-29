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

@environment_threats.route("/", methods=["GET"])
@swag_from({
    'tags': ['Environment Threats'],
    'summary': 'Get environmental threats by UF',
    'description': 'Retrieve the count of different environmental threats in areas of the provided UF.',
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
            'description': 'The environmental threats and their counts successfully retrieved.',
            'schema': {
                'type': 'object',
                'properties': {
                    'uf': {'type': 'string', 'example': 'SP'},
                    'threat_counts': {
                        'type': 'object',
                        'properties': {
                            'Invasões': {'type': 'integer', 'example': 128},
                            'Incêndios': {'type': 'integer', 'example': 152},
                            'Desmatamento Ilegal': {'type': 'integer', 'example': 230},
                            'Nenhuma': {'type': 'integer', 'example': 56}
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
def get_threats():
    uf = request.args.get("uf")
    if not uf:
        return jsonify({"error": "Parâmetro 'uf' é obrigatório"}), 400

    area_names = get_area_names_by_uf(uf)
    threat_counts = get_threat_counts(area_names)

    return jsonify(threat_counts), 200

@environment_threats.route("/threats_by_state", methods=["GET"])
@swag_from({
    'tags': ['Environment Threats'],
    'summary': 'Get environmental threats by state and type',
    'description': 'Retrieve the count of a specific environmental threat by state (UF).',
    'parameters': [
        {
            'name': 'threat_type',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'The type of environmental threat to filter by, e.g., "Invasões", "Incêndios", etc.'
        }
    ],
    'responses': {
        200: {
            'description': 'The environmental threat counts by state successfully retrieved.',
            'schema': {
                'type': 'object',
                'properties': {
                    'threat_counts_by_state': {
                        'type': 'object',
                        'properties': {
                            'SP': {'type': 'integer', 'example': 120},
                            'RJ': {'type': 'integer', 'example': 45},
                            'MG': {'type': 'integer', 'example': 89}
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Invalid threat_type parameter provided.',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Parâmetro "threat_type" é obrigatório!'}
                }
            }
        },
        404: {
            'description': 'No data found for the provided threat type.',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Nenhuma ameaça encontrada para este tipo.'}
                }
            }
        }
    }
})
def count_threats_by_state():
    threat_type = request.args.get("threat_type")
    
    if not threat_type:
        return jsonify({"error": "Parâmetro 'threat_type' é obrigatório"}), 400
     

    areas = db.session.query(Area.area_name, Localization.uf).join(Localization).all()
    area_to_uf = {area.area_name: area.uf for area in areas}

    query = {"environmental_threats": threat_type}
    areas_data = mongo.db.api.find(query)

    threat_counts_by_state = Counter()
    
    for area in areas_data:
        area_name = area["area_name"]
        uf = area_to_uf.get(area_name)

        if uf:
            threat_counts_by_state[uf] += 1

    return jsonify(threat_counts_by_state), 200
