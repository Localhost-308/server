from flask import Blueprint, abort, request
from flask_jwt_extended import jwt_required, create_access_token
import bcrypt

from app.initializer import app
from app.database import db
from app.models import User
from app.schemas import UserSchema, UsuarioRequestDTO, UsuarioResponseDTO

users = Blueprint(
    'users',
    __name__,
    url_prefix=app.config['API_URL_PREFIX'] + '/users'
)

@users.route('/', methods=['GET', 'POST'])
@users.route('/<int:id>', methods=['GET'])
# @jwt_required()
def root(id=None):
    user_query = User.query
    if request.method == 'GET':
        user_list = [User.query.filter_by(id=id).first()] if id else User.query.all()
        user_obj_list = []
        for u in user_list:
            user_obj = UserSchema(exclude=['password', 'cargo']).dump(u)
            user_obj['cargo'] = u.cargo.value
            user_obj_list.append(user_obj)
        
        if not user_obj_list:
            abort(404, description='User not found!')
    
        return user_obj_list
    
    elif request.method == 'POST':
        try:
            data = UsuarioRequestDTO().load(request.json)
        except Exception as e:
            abort(400, description=str(e))

        if User.query.filter_by(email=data['email']).first():
            abort(409, description='E-mail already taken!')

        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=hashed_password.decode('utf-8'),
            cargo=data['cargo']
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            return UsuarioResponseDTO().dump(new_user), 201
        except Exception as e:
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
        "access_token":access_token,
        "user":user_obj
    }
    return response, 200