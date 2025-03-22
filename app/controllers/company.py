from flask import Blueprint, abort, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.initializer import app
from app.database import db
from app.models import Company
from app.schemas import CompanySchema

companies = Blueprint(
    "companies", __name__, url_prefix=app.config["API_URL_PREFIX"] + "/companies"
)


@companies.route("/", methods=["GET"])
@companies.route("/<int:id>", methods=["GET"])
# @jwt_required()
def root(id=None):
    if id:
        company = Company.query.get(id)
        if not company:
            abort(404, description="Company not found!")
        return CompanySchema().dump(company)
    else:
        companies = Company.query.all()
        if not companies:
            abort(404, description="Company not found!")
        return CompanySchema(many=True).dump(companies)


@companies.route("/", methods=["POST"])
@jwt_required()
def post():
    data = request.json
    new_company = Company()
    for field in data:
        setattr(new_company, field, data[field])
    db.session.add(new_company)
    db.session.commit()
    return {"msg": "ok"}


@companies.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete(id):
    company = Company.query.get(id)
    if not company:
        abort(404, description="Company not found!")

    db.session.delete(company)
    db.session.commit()

    return {"message": "Company deleted successfully"}, 200


@companies.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update(id):
    company = Company.query.get(id)
    if not company:
        abort(404, description="Company not found!")

    data = request.get_json()
    if not data:
        abort(400, description="No data provided!")

    try:
        updated_company = CompanySchema().load(data, instance=company, partial=True)
        db.session.commit()
        return CompanySchema().dump(updated_company), 200
    except ValidationError as err:
        return {"errors": err.messages}, 400
