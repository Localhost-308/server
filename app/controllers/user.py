from flasgger import swag_from
from flask import Blueprint, abort, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token
import bcrypt

from app.initializer import app
from app.database import db
from app.models import User
from app.schemas import UserSchema, UsuarioRequestDTO, UsuarioResponseDTO
from app.services.email_service import send_email
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
    user_obj_list = decrypt_user_list(user_list)

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
        data = request.json
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
            cargo=data['cargo'],
            company_id=1
        )
        return UsuarioResponseDTO().dump(new_user), 201
    except Exception as e:
        print(e)
        abort(500, description=str(e).split('\n')[0])


@users.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        abort(400, description='Missing JSON in request!')

    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        abort(400, description='Missing Email and/or Password in request!')

    sqlite_session = get_sqlite_session()
    users = User.query.all()

    for user in users:
        cursor = sqlite_session.execute(
            "SELECT private_key FROM user_keys WHERE user_id = ?", (user.id,)
        )
        result = cursor.fetchone()

        if not result:
            continue

        private_key_pem = result[0]

        try:
            decrypted_email = EncryptionService.decrypt(private_key_pem, user.email)
        except Exception:
            continue  

        if decrypted_email == email:
            if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                sqlite_session.close()
                abort(401, description='Wrong Password!')

            try:
                decrypted_first_name = EncryptionService.decrypt(private_key_pem, user.first_name)
                decrypted_last_name = EncryptionService.decrypt(private_key_pem, user.last_name)
            except Exception:
                sqlite_session.close()
                abort(500, description='Failed to decrypt user name.')

            access_token = create_access_token(identity=user.id, additional_claims={'company_id': user.company_id})

            user_obj = {
                "id": user.id,
                "first_name": decrypted_first_name,
                "last_name": decrypted_last_name,
                "email": decrypted_email,
                "cargo": user.cargo.value
            }

            sqlite_session.close()
            return {
                "access_token": access_token,
                "user": user_obj
            }, 200

    sqlite_session.close()
    abort(404, description='User not found!')


@users.route('/notify-lgpd-incident', methods=['POST'])
@swag_from({
    'tags': ['Notificações'],
    'description': 'Envia notificação de incidente LGPD para todos os usuários.',
    'parameters': [
        {
            'name': 'mensagem',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'mensagem': {
                        'type': 'string',
                        'example': 'Esta é uma notificação de teste do incidente LGPD.'
                    }
                },
                'required': ['mensagem']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'E-mails enviados com sucesso.',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {
                        'type': 'string',
                        'example': 'E-mails enviados com sucesso.'
                    }
                }
            }
        },
        400: {
            'description': 'Erro de validação.',
            'schema': {
                'type': 'object',
                'properties': {
                    'erro': {
                        'type': 'string',
                        'example': 'Campo "mensagem" é obrigatório no corpo da requisição.'
                    }
                }
            }
        }
    }
})
def notify_lgpd_incident():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'erro': 'Campo "mensagem" é obrigatório no corpo da requisição.'}), 400

    message = data['message']
    subject = "Esta menssagem é apenas um teste - DESCONSIDERE"

    encrypted_user_list = User.query.all()
    users = decrypt_user_list(encrypted_user_list)
    email_list = [user["email"] for user in users]

    for email in email_list:
        send_email(recipient=email, subject=subject, body=message)

    return jsonify({'status': 'E-mails enviados com sucesso.'}), 200


def decrypt_user_list(user_list):
    user_obj_list = []

    sqlite_session = get_sqlite_session()

    for u in user_list:
        if u is None:
            continue

        cursor = sqlite_session.execute(
            "SELECT private_key FROM user_keys WHERE user_id = ?", (u.id,)
        )
        result = cursor.fetchone()

        if not result:
            continue

        private_key_pem = result[0]

        try:
            decrypted_first_name = EncryptionService.decrypt(private_key_pem, u.first_name)
            decrypted_last_name = EncryptionService.decrypt(private_key_pem, u.last_name)
            decrypted_email = EncryptionService.decrypt(private_key_pem, u.email)
        except Exception as e:
            print(f"[WARN] Falha ao descriptografar usuário ID {u.id}: {e}")
            continue

        user_obj = {
            "id": u.id,
            "first_name": decrypted_first_name,
            "last_name": decrypted_last_name,
            "email": decrypted_email,
            "cargo": u.cargo.value
        }
        user_obj_list.append(user_obj)

    sqlite_session.close()
    return user_obj_list