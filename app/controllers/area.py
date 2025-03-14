from flask import Blueprint, abort, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

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
