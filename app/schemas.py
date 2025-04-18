from app.initializer import ma
from marshmallow import fields, Schema, validate, validates, ValidationError
from app.models import User, Area, Company, Localization
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
        error_messages={"required": "Nome é obrigatório"}
    )
    last_name = fields.String(
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "Sobrenome é obrigatório"}
    )
    email = fields.Email(
        required=True,
        error_messages={"required": "Email é obrigatório", "invalid": "Email inválido"}
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=6),
        error_messages={"required": "Senha é obrigatória"}
    )
    cargo = fields.String(
        required=True,
        validate=validate.OneOf([e.name for e in CargoEnum]),
        error_messages={"required": "Cargo é obrigatório"}
    )

    @validates("email")
    def validar_email_unico(self, value):
        if User.query.filter_by(email=value).first():
            raise ValidationError("E-mail já está em uso.")


class UsuarioResponseDTO(Schema):
    id = fields.Int()
    first_name = fields.String()
    last_name = fields.String()
    email = fields.Email()
    cargo = fields.String()