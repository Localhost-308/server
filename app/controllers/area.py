from flask import Blueprint, abort, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from flasgger import swag_from
from sqlalchemy import func

from app.util.messages import Messages
from app.initializer import app
from app.database import db
from app.models import Area, Localization
from app.schemas import AreaSchema, AreaExtendedSchema

areas = Blueprint("areas", __name__, url_prefix=app.config["API_URL_PREFIX"] + "/areas")


@areas.route("/", methods=["GET"])
@areas.route("/<int:id>", methods=["GET"])
@jwt_required()
def root(id=None):
    if id:
        area = Area.query.get(id)
        if not area:
            abort(404, description="Area not found!")
        return AreaSchema().dump(area)
    else:
        areas = Area.query.all()
        if not areas:
            abort(404, description="Area not found!")
        return AreaSchema(many=True).dump(areas)


@areas.route("/", methods=["POST"])
@jwt_required()
def post():
    data = request.json
    new_company = Area()
    for field in data:
        setattr(new_company, field, data[field])
    db.session.add(new_company)
    db.session.commit()
    return {"msg": "ok"}


@areas.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete(id):
    area = Area.query.get(id)
    if not area:
        abort(404, description="Area not found!")

    db.session.delete(area)
    db.session.commit()

    return {"message": "Area deleted successfully"}, 200


@areas.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update(id):
    area = Area.query.get(id)
    if not area:
        abort(404, description="Area not found!")

    data = request.get_json()
    if not data:
        abort(400, description="No data provided!")

    try:
        updated_area = AreaSchema().load(data, instance=area, partial=True)
        db.session.commit()
        return AreaSchema().dump(updated_area), 200
    except ValidationError as err:
        return {"errors": err.messages}, 400


@areas.route("/reflorested-area", methods=["GET"])
@swag_from({
    'tags': ['Area Information'],
    'summary': 'Retrieve reflorested area information for specified areas',
    'description': 'Fetches data related to total area, reflorested area, and initially planted area for given areas.',
    'parameters': [
        {
            'name': 'area_id',
            'in': 'query',
            'type': 'integer',
            'description': 'First area ID to filter the data by.',
            'required': False,
            'example': 1
        },
        {
            'name': 'uf',
            'in': 'query',
            'type': 'string',
            'description': 'Federal unit (UF) to filter the areas.',
            'required': False,
            'example': 'SP'
        },
        {
            'name': 'city',
            'in': 'query',
            'type': 'string',
            'description': 'City name to filter the areas.',
            'required': False,
            'example': 'São Paulo'
        }
    ],
    'responses': {
        200: {
            'description': 'Reflorested area information successfully retrieved.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'uf': {'type': 'string', 'example': 'SP'},
                        'city': {'type': 'string', 'example': 'São Paulo'},
                        'area_name': {'type': 'string', 'example': 'Área de Conservação 1'},
                        'total_area_hectares': {'type': 'number', 'example': 150.5},
                        'reflorested_area_hectares': {'type': 'number', 'example': 75.0},
                        'initial_planted_area_hectares': {'type': 'number', 'example': 50.0},
                        'total_reflorested_and_planted': {'type': 'number', 'example': 125.0}
                    }
                }
            }
        },
        400: {
            'description': 'Invalid input data. Ensure area IDs, UF, or city are correct.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': Messages.ERROR_INVALID_DATA('area_id=?, uf=?, city=?')}
                }
            }
        },
        500: {
            'description': 'Internal server error occurred.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': Messages.UNKNOWN_ERROR('Area')}
                }
            }
        }
    }
})
# @jwt_required()
def reflorested_area():
    try:
        params = request.args
        area_id = params.get('area_id', default=None, type=int)
        uf = params.get('uf', default=None, type=str)
        city = params.get('city', default=None, type=str)
        
        areas = db.session.query(
            Localization.uf,
            Localization.city,
            Area.area_name, 
            Area.total_area_hectares, 
            Area.reflorested_area_hectares, 
            Area.initial_planted_area_hectares,
            (Area.reflorested_area_hectares + Area.initial_planted_area_hectares).label('total_reflorested_and_planted')
        ).join(Localization).filter(
            (Area.id == area_id) if area_id else True,
            (func.upper(Localization.uf) == uf.upper()) if uf else True,
            (func.upper(Localization.city) == city.upper()) if city else True
        ).all()

        if not areas:
            abort(400)
        
        return AreaExtendedSchema(many=True).dump(areas)
    
    except Exception as error:
        abort(400, description=Messages.ERROR_INVALID_DATA(f'area_id={area_id_list} or uf={uf}'))
    except Exception as error:
        abort(500, description=Messages.UNKNOWN_ERROR('Area'))
