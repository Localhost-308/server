from flask import Blueprint, abort, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.initializer import app
from app.database import db
from app.models import Localization
from app.schemas import LocalizationSchema

localizations = Blueprint(
    "localizations",
    __name__,
    url_prefix=app.config["API_URL_PREFIX"] + "/localizations",
)


@localizations.route("/", methods=["GET"])
@localizations.route("/<int:id>", methods=["GET"])
# @jwt_required()
def root(id=None):
    if id:
        localization = Localization.query.get(id)
        if not localization:
            abort(404, description="Localization not found!")
        return LocalizationSchema().dump(localization)
    else:
        localizations = Localization.query.all()
        if not localizations:
            abort(404, description="Localization not found!")
        return LocalizationSchema(many=True).dump(localizations)


@localizations.route("/", methods=["POST"])
# @jwt_required()
def post():
    data = request.json
    new_company = Localization()
    for field in data:
        setattr(new_company, field, data[field])
    db.session.add(new_company)
    db.session.commit()
    return {"msg": "ok"}


@localizations.route("/<int:id>", methods=["DELETE"])
# @jwt_required()
def delete(id):
    localization = Localization.query.get(id)
    if not localization:
        abort(404, description="Localization not found!")

    db.session.delete(localization)
    db.session.commit()

    return {"message": "Localization deleted successfully"}, 200


@localizations.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update(id):
    localization = Localization.query.get(id)
    if not localization:
        abort(404, description="Area not found!")

    data = request.get_json()
    if not data:
        abort(400, description="No data provided!")

    try:
        updated_localization = LocalizationSchema().load(
            data, instance=localization, partial=True
        )
        db.session.commit()
        return LocalizationSchema().dump(updated_localization), 200
    except ValidationError as err:
        return {"errors": err.messages}, 400
