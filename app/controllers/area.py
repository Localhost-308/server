from flask import Blueprint, abort, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from flasgger import swag_from

from app.util.messages import Messages
from app.initializer import app
from app.database import db
from app.models import Area
from app.schemas import AreaSchema

areas = Blueprint("areas", __name__, url_prefix=app.config["API_URL_PREFIX"] + "/areas")


@areas.route("/", methods=["GET"])
@areas.route("/<int:id>", methods=["GET"])
# @jwt_required()
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
            'description': 'ID of the area to filter the data by.',
            'required': False
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
                        'area_name': {'type': 'string', 'example': 'Área de Conservação 1'},
                        'total_area_hectares': {'type': 'number', 'example': 150.5},
                        'reflorested_area_hectares': {'type': 'number', 'example': 75.2},
                        'initial_planted_area_hectares': {'type': 'number', 'example': 50.0},
                        'total_reflorested_and_planted': {'type': 'number', 'example': 125.2}
                    }
                }
            }
        },
        400: {
            'description': 'Invalid input data. Ensure the area ID is correct.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': Messages.ERROR_INVALID_DATA('area_id=?')}
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
        areas = []
        params = request.args
        area_id = params.get('area_id', None)
        print(area_id)
        if area_id:
            area = Area.query.get(area_id)
            if area:
                areas.append(area)
        else:
            areas = Area.query.all()
        
        print(areas)
        
        # if not areas:
        #     abort(400)
        
        result = []
        for area in areas:
            total_area = area.total_area_hectares
            reflorested_area = area.reflorested_area_hectares
            initial_planted_area = area.initial_planted_area_hectares
            result.append({
                "area_name": area.area_name,
                "total_area_hectares": total_area,
                "reflorested_area_hectares": reflorested_area,
                "initial_planted_area_hectares": initial_planted_area,
                "total_reflorested_and_planted": reflorested_area + initial_planted_area
            })
        
        return jsonify(result)
    
    except Exception as error:
        abort(400, description=Messages.ERROR_INVALID_DATA(f'area_id={area_id}'))
    except Exception as error:
        abort(500, description=Messages.UNKNOWN_ERROR('Area'))
