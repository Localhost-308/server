from app.initializer import ma
from marshmallow import fields
from app.models import User, Area, Company, Localization
from app.util.utils import get_city_coordinates


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


class AreaGeoSchema(ma.SQLAlchemyAutoSchema):
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
        print(area.keys())
        return get_city_coordinates(area['city'])