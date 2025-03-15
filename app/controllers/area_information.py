from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
from flask import Blueprint, abort, request, jsonify

from app.util.messages import Messages
from app.schemas import CompanySchema
from app.initializer import app, mongo


area_information = Blueprint(
    "area_information", __name__, url_prefix=app.config["API_URL_PREFIX"] + "/area-information"
)

@area_information.route("/", methods=["GET"])
# @jwt_required()
def get_all():
    area_info = list(mongo.db.api.find({}, {"_id": 0}))
    if not area_info:
        abort(404, description=Messages.ERROR_NOT_FOUND('Area Information'))
    return jsonify(area_info)

@area_information.route("/<int:area_id>", methods=["GET"])
# @jwt_required()
def get_by_area_id(area_id):
    
    a = 1

    return ''

@area_information.route("/", methods=["POST"])
# @jwt_required()
def post():
    data = request.json
    if not data:
        abort(404, description=Messages.ERROR_INVALID_DATA('Area Information'))
        # return jsonify({"error": "Dados inválidos"}), 400

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
