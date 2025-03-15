from flask import Flask, request, Response
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_cors import CORS
from flask_pymongo import PyMongo

from app.models import User
from app.config import Config
from app.database import db

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
cors = CORS(app, resources={r"*": {"origins": "*"}})
mongo = PyMongo(app, uri=app.config["MONGO_URI"])

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'user': User,
        'mongo': mongo
    }

with app.app_context():
    db.create_all()

@app.before_request
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()
