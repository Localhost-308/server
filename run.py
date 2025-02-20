from app.controllers import user
from app.initializer import app

app.register_blueprint(user.users)