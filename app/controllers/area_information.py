from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
from flask import Blueprint, abort, request, jsonify
from flasgger import swag_from

from datetime import datetime
from app.util.messages import Messages
from app.initializer import app, mongo

area_information = Blueprint(
    "area_information", __name__, url_prefix=app.config["API_URL_PREFIX"] + "/area-information"
)

@area_information.route("/", methods=["GET"])
# @jwt_required()
@swag_from({
    'tags': ['Area Information'],
    'summary': 'Get filtered area information',
    'description': 'Retrieve area information based on optional filters like area_id and date range.',
    'parameters': [
        {
            'name': 'area_id',
            'in': 'query',
            'required': False,
            'schema': {'type': 'integer'},
            'description': 'The ID of the area'
        },
        {
            'name': 'start_date',
            'in': 'query',
            'required': False,
            'schema': {'type': 'string', 'format': 'date'},
            'description': 'Start date for filtering (YYYY-MM-DD)'
        },
        {
            'name': 'end_date',
            'in': 'query',
            'required': False,
            'schema': {'type': 'string', 'format': 'date'},
            'description': 'End date for filtering (YYYY-MM-DD)'
        }
    ],
    'responses': {
        200: {
            'description': 'Aggregated tree information successfully retrieved.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'measurement_date': {'type': 'string', 'example': '2025-03-19'},
                        'total_avoided_co2': {'type': 'number', 'example': 164.3}
                    }
                }
            }
        },
        400: {
            'description': 'Invalid input data. Ensure the area ID and dates are correct.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': Messages.ERROR_INVALID_DATA('Area Information')}
                }
            }
        },
        500: {
            'description': 'Internal server error occurred.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': Messages.UNKNOWN_ERROR('Area Information')}
                }
            }
        }
    }
})
def get_all_by():
    try:
        filters = {}
        params = request.args.to_dict()

        if 'area_id' in params:
            filters['area_id'] = int(params['area_id'])

        if 'start_date' in params or 'end_date' in params:
            filters['measurement_date'] = {
                "$gte": params['start_date'],
                "$lt": params['end_date']
            }

        pipeline = [
            {"$match": filters},
            {
                "$group": {
                    "_id": {"$substr": ["$measurement_date", 0, 7]},
                    "total_avoided_co2": {"$sum": "$avoided_co2_emissions_m3"}
                }
            },
            {"$sort": {"_id": 1}},
            {"$project": {"_id": 0, "measurement_date": "$_id", "total_avoided_co2": 1}}
        ]

        area_info = list(mongo.db.api.aggregate(pipeline))
        return jsonify(area_info)

    except KeyError as error:
        abort(400, description=Messages.ERROR_INVALID_DATA('Area Information'))
    except Exception as error:
        abort(500, description=Messages.UNKNOWN_ERROR('Area Information'))


@area_information.route("/", methods=["POST"])
# @jwt_required()
@swag_from({
    'tags': ['Area Information'],
    'summary': 'Create a new area information entry',
    'description': 'Add a new area information record to the database.',
    'responses': {
        201: {'description': 'Area information created successfully'},
        400: {'description': Messages.ERROR_INVALID_DATA('Area Information')}
    }
})
def save_area_information():
    data = request.json
    if not data:
        abort(400, description=Messages.ERROR_INVALID_DATA('Area Information'))

    mongo.db.api.insert_one(data)
    return jsonify({"msg": Messages.SUCCESS_SAVE_SUCCESSFULLY('Area Information')})


@area_information.route("/tree", methods=["GET"])
# @jwt_required()
@swag_from({
    'tags': ['Area Information'],
    'summary': 'Retrieve area information on tree measurements',
    'description': 'Fetches aggregated data on tree measurements (such as number of trees lost, growth, etc.) for a given area and date range.',
    'parameters': [
        {
            'name': 'area_id',
            'in': 'query',
            'type': 'integer',
            'description': 'ID of the area to filter the data by.',
            'required': False
        },
        {
            'name': 'start_date',
            'in': 'query',
            'type': 'string',
            'format': 'date',
            'description': 'Start date of the date range to filter the data (YYYY-MM-DD). Default is 2000-01-01.',
            'required': False
        },
        {
            'name': 'end_date',
            'in': 'query',
            'type': 'string',
            'format': 'date',
            'description': 'End date of the date range to filter the data (YYYY-MM-DD). Default is the current date.',
            'required': False
        }
    ],
    'responses': {
        200: {
            'description': 'Aggregated tree information successfully retrieved.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'measurement_date': {'type': 'string', 'example': '2025-03-19'},
                        'total_number_of_trees_lost': {'type': 'integer', 'example': 12042},
                        'total_average_tree_growth_cm': {'type': 'number', 'example': 164.3},
                        'total_trees_alive_so_far': {'type': 'integer', 'example': 54884},
                        'total_tree_survival_rate': {'type': 'number', 'example': 82.00}
                    }
                }
            }
        },
        400: {
            'description': 'Invalid input data. Ensure the area ID and dates are correct.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': Messages.ERROR_INVALID_DATA('Area Information')}
                }
            }
        },
        500: {
            'description': 'Internal server error occurred.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': Messages.UNKNOWN_ERROR('Area Information')}
                }
            }
        }
    }
})
def get_tree_information():
    try:
        filters = {}
        params = request.args

        area_id = params.get('area_id', False)
        start_date = params.get('start_date', '2000-01-01')
        end_date = params.get('end_date', str(datetime.now().strftime('%Y-%m-%d')))

        msg = {
            'area id': area_id,
            'start date': start_date,
            'end date': end_date
        }

        if params.get('area_id', False):
            filters['area_id'] = int(params['area_id'])

        if start_date or end_date:
            filters['measurement_date'] = {
                "$gte": start_date,
                "$lt": end_date
            }

        pipeline = [
            {"$match": filters},
            {
                "$group": {
                    "_id": {"$substr": ["$measurement_date", 0, 7]},
                    "total_number_of_trees_lost": {"$sum": "$number_of_trees_lost"},
                    "total_average_tree_growth_cm": {"$sum": "$average_tree_growth_cm"},
                    "total_trees_alive_so_far": {"$sum": "$trees_alive_so_far"},
                    "total_tree_survival_rate": {"$sum": "$tree_survival_rate"}
                }
            },
            {"$sort": {"_id": 1}},
            {"$project": {
                "_id": 0, 
                "measurement_date": "$_id", 
                "total_number_of_trees_lost": 1,
                "total_average_tree_growth_cm": 1,
                "total_trees_alive_so_far": 1,
                "total_tree_survival_rate": 1
                }}
        ]

        tree_info = list(mongo.db.api.aggregate(pipeline))
        return jsonify(tree_info)

    except KeyError as error:
        abort(400, description=Messages.ERROR_INVALID_DATA('Area Information'))
    except Exception as error:
        abort(500, description=Messages.UNKNOWN_ERROR('Area Information'))

