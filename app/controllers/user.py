from flasgger import swag_from
from flask import Blueprint, abort, request
from flask_jwt_extended import jwt_required, create_access_token
import bcrypt

from app.initializer import app
from app.database import db
from app.models import User
from app.schemas import UserSchema, UsuarioRequestDTO, UsuarioResponseDTO
from app.services.user_service import UserService
from app.services.encryption_service import EncryptionService
from app.database.sqlite import get_sqlite_session

users = Blueprint(
    'users',
    __name__,
    url_prefix=app.config['API_URL_PREFIX'] + '/users'
)

@users.route('/', methods=['GET'])
@swag_from({
    'summary': 'Retrieve users',
    'description': 'Returns a list of all users or details of a specific user if ID is provided.',
    'parameters': [
        {
            'name': 'id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'ID of the user to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'Successful retrieval of users',
            'content': {
                'application/json': {
                    'example': [
                        {
                            'id': 1,
                            'first_name': 'John',
                            'last_name': 'Doe',
                            'email': 'john.doe@example.com',
                            'cargo': 'admin'
                        }
                    ]
                }
            }
        },
        404: {
            'description': 'User not found'
        }
    }
})
@jwt_required()
def get_users():
    id = request.args.get('id', type=int)
    user_list = [User.query.filter_by(id=id).first()] if id else User.query.all()
    user_obj_list = []

    sqlite_session = get_sqlite_session()

    for u in user_list:
        if u is None:
            continue

        cursor = sqlite_session.execute(
            "SELECT private_key FROM user_keys WHERE user_id = ?", (u.id,)
        )
        result = cursor.fetchone()

        if result:
            private_key_pem = result[0]

            decrypted_first_name = EncryptionService.decrypt(private_key_pem, u.first_name)
            decrypted_last_name = EncryptionService.decrypt(private_key_pem, u.last_name)
            decrypted_email = EncryptionService.decrypt(private_key_pem, u.email)

            user_obj = {
                "id": u.id,
                "first_name": decrypted_first_name,
                "last_name": decrypted_last_name,
                "email": decrypted_email,
                "cargo": u.cargo.value
            }
            user_obj_list.append(user_obj)

    sqlite_session.close()

    if not user_obj_list:
        abort(404, description='User not found!')

    return user_obj_list, 200


@users.route('/<int:id>', methods=['DELETE'])
@swag_from({
    'summary': 'Delete a user',
    'description': 'Deletes a user based on the provided ID.',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the user to delete'
        }
    ],
    'responses': {
        200: {
            'description': 'User successfully deleted'
        },
        400: {
            'description': 'User ID is required for deletion'
        },
        404: {
            'description': 'User not found'
        }
    }
})
@jwt_required()
def delete_user(id):
    if id is None:
        abort(400, description='User ID is required for deletion.')

    success = UserService.delete_user(id)

    if not success:
        abort(404, description='User not found!')

    return {"message": "User and private key successfully deleted."}, 200


@users.route('/', methods=['POST'])
@swag_from({
    'summary': 'Create a new user',
    'description': 'Creates a user with the provided information.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'first_name': {'type': 'string'},
                    'last_name': {'type': 'string'},
                    'email': {'type': 'string'},
                    'password': {'type': 'string'},
                    'cargo': {'type': 'string'}
                },
                'example': {
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john.doe@example.com',
                    'password': 'Password123!',
                    'cargo': 'ADMIN'
                }
            }
        }
    ],
    'responses': {
        201: {'description': 'User successfully created'},
        400: {'description': 'Invalid request'},
        409: {'description': 'E-mail already taken'},
        500: {'description': 'Internal server error'}
    }
})
def create_user():
    try:
        data = UsuarioRequestDTO().load(request.json)
    except Exception as e:
        abort(400, description=str(e))

    if User.query.filter_by(email=data['email']).first():
        abort(409, description='E-mail already taken!')

    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

    try:
        new_user = UserService.create_user(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=hashed_password.decode('utf-8'),
            cargo=data['cargo']
        )
        return UsuarioResponseDTO().dump(new_user), 201
    except Exception as e:
        print(e)
        abort(500, description=str(e).split('\n')[0])


@users.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        abort(400, description='Missing JSON in request!')

    email = request.json.get('email', None)
    password = request.json.get('password', None)
    
    if not email or not password:
        abort(400, description='Missing Email and/or Password in request!')
    
    user = User.query.filter_by(email=email).one_or_none()
    if not user:
        abort(404, description='User not found!')

    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        abort(401, description='Wrong Password!')

    access_token = create_access_token(identity=user.id)
    user_obj = UserSchema(exclude=['password', 'cargo']).dump(user)
    user_obj['cargo'] = user.cargo.value
    response = {
        "access_token": access_token,
        "user": user_obj
    }
    return response, 200
