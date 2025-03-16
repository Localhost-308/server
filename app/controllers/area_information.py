from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
from flask import Blueprint, abort, request, jsonify
from flasgger import swag_from

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
            'description': 'Aggregated area information based on the provided filters',
            'content': {
                'application/json': {
                    'example': [
                        {
                            "measurement_date": "2024-02",
                            "total_avoided_co2": 1500.5
                        }
                    ]
                }
            }
        },
        400: {
            'description': Messages.ERROR_INVALID_DATA('Area Information')
        },
        500: {
            'description': Messages.UNKNOWN_ERROR('Area Information')
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
