from app.initializer import ma
from marshmallow import fields, Schema, validate, validates, ValidationError
from app.models import User, Area, Company, Localization
from app.util.utils import get_city_coordinates

from app.models.user import CargoEnum

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True


class CompanySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Company
        load_instance = True


class LocalizationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Localization
        load_instance = True


class AreaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Area
        load_instance = True


class AreaListSchema(ma.SQLAlchemyAutoSchema):
    id = fields.Int()
    area_name = fields.Str()


class AreaExtendedSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Area
        load_instance = True
    uf = fields.Str()
    city = fields.Str()
    quantity = fields.Str()
    company_name = fields.Str()
    created_on_month = fields.Str()
    total_reflorested_and_planted = fields.Float()

class UsuarioRequestDTO(Schema):
    first_name = fields.String(
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "First name is required"}
    )
    last_name = fields.String(
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "Last name is required"}
    )
    email = fields.Email(
        required=False,
        error_messages={"required": "Email is required", "invalid": "Email inválido"}
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=6),
        error_messages={"required": "Password is required"}
    )
    cargo = fields.String(
        required=True,
        validate=validate.OneOf([e.name for e in CargoEnum]),
        error_messages={"required": "Job title is required"}
    )

class UsuarioResponseDTO(ma.SQLAlchemyAutoSchema):
    id = fields.Int()
    first_name = fields.String()
    last_name = fields.String()
    email = fields.Email()
    cargo = fields.String()


class AreaGeoSchema(ma.SQLAlchemyAutoSchema):
    area_id = fields.Int()
    area_name = fields.Str()
    company_name = fields.Str()
    uf = fields.Str()
    city = fields.Str()
    total_area_hectares = fields.Float()
    reflorested_area_hectares = fields.Float()
    number_of_trees_planted = fields.Float()
    tree_health_status = fields.Str()
    stage_indicator = fields.Str()
    tree_survival_rate = fields.Float()
    coordinates = fields.Method("get_coordinates")

    def get_coordinates(self, area):
        return get_city_coordinates(area['city'])