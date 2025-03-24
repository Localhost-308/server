from app.initializer import ma
from marshmallow import fields
from app.models import User, Area, Company, Localization


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

class AreaExtendedSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Area
        load_instance = True
    uf = fields.Str()
    city = fields.Str()
    total_reflorested_and_planted = fields.Float()
