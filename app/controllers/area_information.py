from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
from flask import Blueprint, abort, request, jsonify
from flasgger import swag_from

from app.util.messages import Messages
from app.schemas import CompanySchema
from app.initializer import app, mongo

area_information = Blueprint(
    "area_information", __name__, url_prefix=app.config["API_URL_PREFIX"] + "/area-information"
)

@area_information.route("/", methods=["GET"])
# @jwt_required()
@swag_from({
    'tags': ['Area Information'],
    'summary': 'Get all area information',
    'description': 'Returns information about the area, including CO2 avoided, tree growth, water availability and a lot of other information about the area.',
    'responses': {
        200: {
            'description': 'A list of area information',
        },
        404: {
            'description': Messages.ERROR_NOT_FOUND('Area Information')
        }
    }
})
def get_all():
    area_info = list(mongo.db.api.find({}, {"_id": 0}))
    if not area_info:
        abort(404, description=Messages.ERROR_NOT_FOUND('Area Information'))
    return jsonify(area_info)

@area_information.route("/<int:area_id>", methods=["GET"])
# @jwt_required()
def get_by_area_id(area_id):
    area_info = list(mongo.db.api.find({"area_id":area_id}, {"_id": 0}))
    if not area_info:
        abort(404, description=Messages.ERROR_NOT_FOUND('Area Information'))
    return jsonify(area_info)

@area_information.route("/", methods=["POST"])
# @jwt_required()
def post():
    data = request.json
    if not data:
        abort(404, description=Messages.ERROR_INVALID_DATA('Area Information'))

    mongo.db.api.insert_one(data)
    return jsonify({"msg": Messages.SUCCESS_SAVE_SUCCESSFULLY('Area Information')})

# @area_information.route("/<int:id>", methods=["DELETE"])
# # @jwt_required()
# def delete(id):
#     company = Company.query.get(id)
#     if not company:
#         abort(404, description="Company not found!")

#     db.session.delete(company)
#     db.session.commit()

#     return {"message": "Company deleted successfully"}, 200

# @area_information.route("/<int:id>", methods=["PUT"])
# # @jwt_required()
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
