from flask_cors import CORS
from flasgger import Swagger
from flask_migrate import Migrate
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask import Flask, request, Response

from app.models import User, TermsAcceptance, TermsAndCondition
from app.database import db
from app.config import Config
# from app.util.chat import Chat
# from app.util.report_messages import chat_template

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
swagger = Swagger(app)
cors = CORS(app, resources={r"*": {"origins": "*"}})
mongo = PyMongo(app, uri=app.config["MONGO_URI"])
# chat = Chat()
# chat.send_message(chat_template)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'user': User,
        'terms_acceptance': TermsAcceptance,
        'terms_and_condition': TermsAndCondition,
        'mongo': mongo
    }

with app.app_context():
    db.create_all()

@app.before_request
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()
