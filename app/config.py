import os

def gen_connection_string():
    db_addr = os.environ.get('DB_ADDR')
    db_name = os.environ.get('DB_NAME')
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')

    return 'postgresql://%s:%s@%s:5432/%s' \
        % (db_user, db_password, db_addr, db_name)

class Config:
    SQLALCHEMY_DATABASE_URI = gen_connection_string()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    API_URL_PREFIX = '/api/v0'