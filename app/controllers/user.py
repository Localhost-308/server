from flask import Blueprint, abort, request
from flask_jwt_extended import jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
# from uuid import uuid4

from app.initializer import app
from app.database import db
from app.models import User
from app.schemas import UserSchema

users = Blueprint(
    'users',
    __name__,
    url_prefix=app.config['API_URL_PREFIX'] + '/users'
)

@users.route('/', methods=['GET', 'POST'])
@users.route('/<int:id>', methods=['GET'])
@jwt_required()
def root(id=None):
    user_query = User.query
    if request.method == 'GET':
        result = UserSchema(exclude=['password']).dump(user_query.get(id)) \
            if id else [UserSchema(exclude=['password']).dump(u) for u in user_query.all()]
        if not result:
            abort(404, description='User not found!')
        return result
    elif request.method == 'POST':
        data = request.json
        new_user = User()
        for field in data:
            setattr(new_user, field, data[field])
        if new_user.email and User.query.filter_by(email=new_user.email).one_or_none():
            abort(409, description='E-mail already taken!')
        new_user.password = generate_password_hash(new_user.password)
        try:
            db.session.add(new_user)
            db.session.commit()
            return UserSchema(exclude=['password']).dump(new_user)
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
    if not check_password_hash(str(user.password), password):
        abort(401, description='Wrong Password!')
    access_token = create_access_token(identity=user.id, additional_claims={'company_id': user.company_id})
    response = {
        "access_token":access_token,
        "user":UserSchema(exclude=['password']).dump(User.query.filter_by(id=user.id).one())
    }
    return response, 200