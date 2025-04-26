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

@users.route('/', methods=['GET', 'POST'])
@users.route('/<int:id>', methods=['GET', 'DELETE'])
# @jwt_required()
def root(id=None):
    if request.method == 'GET':
        user_list = [User.query.filter_by(id=id).first()] if id else User.query.all()
        user_obj_list = []

        sqlite_session = get_sqlite_session()

        for u in user_list:
            if u is None:
                continue

            # Busca a chave privada do usuário no SQLite
            cursor = sqlite_session.execute(
                "SELECT private_key FROM user_keys WHERE user_id = ?", (u.id,)
            )
            result = cursor.fetchone()

            if result:
                private_key_pem = result[0]

                # Descriptografa os campos
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

    elif request.method == 'POST':
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
            abort(500, description=str(e).split('\n')[0])

    elif request.method == 'DELETE':
        if id is None:
            abort(400, description='User ID is required for deletion.')

        success = UserService.delete_user(id)

        if not success:
            abort(404, description='User not found!')

        return {"message": "User and private key successfully deleted."}, 200

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
