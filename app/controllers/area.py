from flask import Blueprint, abort, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from flasgger import swag_from
from sqlalchemy import func, cast, Date
from datetime import datetime

from app.util.messages import Messages
from app.initializer import app
from app.database import db
from app.models import Area, Localization, Company
from app.schemas import AreaSchema, AreaExtendedSchema, AreaListSchema

areas = Blueprint("areas", __name__, url_prefix=app.config["API_URL_PREFIX"] + "/areas")


@areas.route("/", methods=["GET"])
@areas.route("/<int:id>", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Area Information'],
    'summary': 'Retrieve area information',
    'description': 'Fetches information about all areas, filters by city, or retrieves a specific area by ID.',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'description': 'ID of the area to retrieve.',
            'required': False,
            'example': 1
        },
        {
            'name': 'city',
            'in': 'query',
            'type': 'string',
            'description': 'Filter areas by city name.',
            'required': False,
            'example': 'São Paulo'
        }
    ],
    'responses': {
        200: {
            'description': 'Successfully retrieved area information.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'number_of_trees_planted': {'type': 'integer', 'example': 5000},
                        'planting_techniques': {'type': 'string', 'example': 'Direct seeding, seedling planting'},
                        'reflorested_area_hectares': {'type': 'number', 'example': 120.0},
                        'total_area_hectares': {'type': 'number', 'example': 200.5},
                        'planted_species': {'type': 'string', 'example': 'Ipê, Jacarandá, Pau-Brasil'},
                        'initial_vegetation_cover': {'type': 'string', 'example': 'Degraded pasture'},
                        'initial_planted_area_hectares': {'type': 'number', 'example': 50.0},
                        'city': {'type': 'string', 'example': 'São Paulo'},
                        'uf': {'type': 'string', 'example': 'SP'}
                    }
                }
            }
        },
        404: {
            'description': 'Area not found.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Area not found!'}
                }
            }
        }
    }
})
def root(id=None):
    city_filter = request.args.get('city')
    if id:
        area = Area.query.get(id)
        if not area:
            abort(404, description="Area not found!")
            
        localization = Localization.query.get(area.localization_id)

        return jsonify({
        "number_of_trees_planted": area.number_of_trees_planted,
        "planting_techniques":area.planting_techniques,
        "reflorested_area_hectares": area.reflorested_area_hectares,
        "total_area_hectares": area.total_area_hectares,
        "planted_species": area.planted_species,
        "initial_vegetation_cover": area.initial_vegetation_cover,
        "initial_planted_area_hectares": area.initial_planted_area_hectares,
        "city": localization.city,
        "uf": localization.uf,
    })

    else:
        query = Area.query

        if city_filter:
            query = query.join(Localization).filter(Localization.city == city_filter)
        
        area = query.first()
        if not area:
            abort(404, description="Area not found!")
        localization = Localization.query.get(area.localization_id)

        return jsonify({
        "number_of_trees_planted": area.number_of_trees_planted,
        "planting_techniques": area.planting_techniques,
        "reflorested_area_hectares": area.reflorested_area_hectares,
        "total_area_hectares": area.total_area_hectares,
        "planted_species": area.planted_species,
        "initial_vegetation_cover": area.initial_vegetation_cover,
        "initial_planted_area_hectares": area.initial_planted_area_hectares,
        "city": localization.city,
        "uf": localization.uf,
    })

@areas.route("/list", methods=["GET"])
@jwt_required()
def get_area_list():
    areas = Area.query.all()
    if not areas:
        abort(404, description="Area not found!")
    return AreaListSchema(many=True).dump(areas)


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
@jwt_required()
def reflorested_area():
    params = request.args
    area_id = params.get('area_id', default=None, type=int)
    uf = params.get('uf', default=None, type=str)
    city = params.get('city', default=None, type=str)
    try:
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
        abort(400, description=Messages.ERROR_INVALID_DATA(f'area_id={area_id} or uf={uf} or city={city}'))
    except Exception as error:
        abort(500, description=Messages.UNKNOWN_ERROR('Area'))


@areas.route("/planted-species", methods=["GET"])
@swag_from({
    'tags': ['Area Information'],
    'summary': 'Retrieve planted species information for specified areas',
    'description': 'Fetches data related to planted species, the area, and company information for given areas, filtered by optional parameters like area_id, uf, city, company name, and date range.',
    'parameters': [
        {
            'name': 'area_id',
            'in': 'query',
            'type': 'integer',
            'description': 'Area ID to filter the data by.',
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
        },
        {
            'name': 'company_name',
            'in': 'query',
            'type': 'string',
            'description': 'Company name to filter the areas.',
            'required': False,
            'example': 'EcoTech'
        },
        {
            'name': 'start_date',
            'in': 'query',
            'type': 'string',
            'format': 'date',
            'description': 'Start date to filter the creation date of the areas.',
            'required': False,
            'example': '2020-01-01'
        },
        {
            'name': 'end_date',
            'in': 'query',
            'type': 'string',
            'format': 'date',
            'description': 'End date to filter the creation date of the areas.',
            'required': False,
            'example': '2025-01-01'
        }
    ],
    'responses': {
        200: {
            'description': 'Planted species information successfully retrieved.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'uf': {'type': 'string', 'example': 'SP'},
                        'city': {'type': 'string', 'example': 'São Paulo'},
                        'company_name': {'type': 'string', 'example': 'EcoTech'},
                        'area_name': {'type': 'string', 'example': 'Área de Conservação 1'},
                        'planted_species': {'type': 'array', 'items': {'type': 'string'}, 'example': ['Espécie 1', 'Espécie 2']},
                        'created_on_month': {'type': 'string', 'example': '2023-05'}
                    }
                }
            }
        },
        400: {
            'description': 'Invalid input data. Ensure area IDs, UF, city, company name, or dates are correct.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': Messages.ERROR_INVALID_DATA('area_id=?, uf=?, city=?, company_name=?, start_date=?, end_date=?')}
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
@jwt_required()
def planted_species():
    try:
        params = request.args
        area_id = params.get('area_id', default=None, type=int)
        uf = params.get('uf', default=None, type=str)
        city = params.get('city', default=None, type=str)
        company_name = params.get('company_name', default=None, type=str)
        start_date = datetime.strptime(params.get('start_date', default='2000-01-01', type=str), "%Y-%m-%d")
        end_date = datetime.strptime(params.get('end_date', default=datetime.now().strftime('%Y-%m-%d'), type=str), "%Y-%m-%d")
        
        areas = db.session.query(
            Localization.uf,
            Localization.city,
            (Company.name).label('company_name'),
            Area.area_name,
            Area.planted_species,
            func.to_char(Area.created_on, 'YYYY-MM').label('created_on_month')
        ).join(Localization).join(Company).filter(
            (Area.id == area_id) if area_id else True,
            (func.upper(Localization.uf) == uf.upper()) if uf else True,
            (func.upper(Localization.city) == city.upper()) if city else True,
            (func.upper(Company.name) == company_name.upper()) if company_name else True,
            cast(Area.created_on, Date) >= start_date,
            cast(Area.created_on, Date) <= end_date
        ).all()

        if not areas:
            abort(400)
        
        areas_result = AreaExtendedSchema(many=True).dump(areas)

        for area in areas_result:
            area['planted_species'] = str(area['planted_species']).split(', ')
        
        return areas_result
    
    except Exception as error:
        print('ERROR: ',error)
        abort(400, description=Messages.ERROR_INVALID_DATA(f'area_id={area_id} or uf={uf} or city={city} or '\
                                                           f'company_name={company_name} or start_date={start_date} or end_date={end_date}'))
    except Exception as error:
        abort(500, description=Messages.UNKNOWN_ERROR('Area'))

