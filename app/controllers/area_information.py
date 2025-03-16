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

# @area_information.route("/<int:area_id>", methods=["GET"])
# # @jwt_required()
# @swag_from({
#     'tags': ['Area Information'],
#     'summary': 'Get area information by ID',
#     'description': 'Retrieve specific area information based on the provided area_id.',
#     'parameters': [
#         {'name': 'area_id', 'in': 'path', 'required': True, 'type': 'integer', 'description': 'The ID of the area'}
#     ],
#     'responses': {
#         200: {'description': 'Area information retrieved successfully'},
#         404: {'description': Messages.ERROR_NOT_FOUND('Area Information')}
#     }
# })
# def get_by_area_id(area_id):
#     area_info = list(mongo.db.api.find({"area_id": area_id}, {"_id": 0, "avoided_co2_emissions_m3": 1, "measurement_date": 1}))
#     if not area_info:
#         abort(404, description=Messages.ERROR_NOT_FOUND('Area Information'))
#     return jsonify(area_info)


# @area_information.route("/<int:area_id><str:date>", methods=["GET"])
# @jwt_required()
# @swag_from({
#     'tags': ['Area Information'],
#     'summary': 'Get area information by ID',
#     'description': 'Retrieve specific area information based on the provided area_id.',
#     'parameters': [
#         {'name': 'area_id', 'in': 'path', 'required': True, 'type': 'integer', 'description': 'The ID of the area'}
#     ],
#     'responses': {
#         200: {'description': 'Area information retrieved successfully'},
#         404: {'description': Messages.ERROR_NOT_FOUND('Area Information')}
#     }
# })
# @area_information.route("/", methods=["GET"])
# def get_by_area_filters():
    # area_info = list(mongo.db.api.find({"area_id": area_id, "measurement_date": date}, {"_id": 0, "avoided_co2_emissions_m3": 1, "measurement_date": 1}))
    # if not area_info:
    #     abort(404, description=Messages.ERROR_NOT_FOUND('Area Information'))
    # area_id = request.args.get("area_id", type=int)
    # date = request.args.get("date", type=str)
    # return f"Area ID: {area_id}, Date: {date}"
    # return jsonify(area_info)


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
def post():
    data = request.json
    if not data:
        abort(400, description=Messages.ERROR_INVALID_DATA('Area Information'))

    mongo.db.api.insert_one(data)
    return jsonify({"msg": Messages.SUCCESS_SAVE_SUCCESSFULLY('Area Information')})


# @area_information.route("/<int:id>", methods=["DELETE"])
# # @jwt_required()
# @swag_from({
#     'tags': ['Area Information'],
#     'summary': 'Delete an area information entry',
#     'description': 'Remove a specific area information record from the database.',
#     'parameters': [
#         {'name': 'id', 'in': 'path', 'required': True, 'type': 'integer', 'description': 'The ID of the record to delete'}
#     ],
#     'responses': {
#         200: {'description': 'Record deleted successfully'},
#         404: {'description': 'Company not found'}
#     }
# })
# def delete(id):
#     company = Company.query.get(id)
#     if not company:
#         abort(404, description="Company not found!")

#     db.session.delete(company)
#     db.session.commit()

#     return {"message": "Company deleted successfully"}, 200


# @area_information.route("/<int:id>", methods=["PUT"])
# # @jwt_required()
# @swag_from({
#     'tags': ['Area Information'],
#     'summary': 'Update an area information entry',
#     'description': 'Modify an existing area information record.',
#     'parameters': [
#         {
#             'name': 'id',
#             'in': 'path',
#             'required': True,
#             'schema': {'type': 'integer'},
#             'description': 'The ID of the record to update'
#         }
#     ],
#     'responses': {
#         200: {'description': 'Record updated successfully'},
#         400: {'description': 'Invalid data provided'},
#         404: {'description': 'Company not found'}
#     }
# })
# def update(id):
#     company = Company.query.get(id)
#     if not company:
#         abort(404, description="Company not found!")

#     data = request.get_json()
#     if not data:
#         abort(400, description="No data provided!")

#     try:
#         updated_company = CompanySchema().load(data, instance=company, partial=True)
#         db.session.commit()
#         return CompanySchema().dump(updated_company), 200
#     except ValidationError as err:
#         return {"errors": err.messages}, 400
