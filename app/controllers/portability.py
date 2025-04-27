import os
import jwt
import secrets
import datetime
import pandas as pd
from sqlalchemy import func
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask import Blueprint, abort, request, jsonify

from app.database import db
from app.initializer import app, mongo
from app.util.messages import Messages
from app.models import Area, Company, Localization

portability = Blueprint("portability", __name__, url_prefix=app.config["API_URL_PREFIX"] + "/portability")

@portability.route("/", methods=["GET"])
@jwt_required()
def get_user_info():
    try:
        claims = get_jwt()
        company_id = claims.get('company_id')

        sql_query = db.session.query(
            (Area.id).label('areaid'), Area.area_name, Localization.uf, Localization.city
        ).join(Company).join(Localization).filter(
            Company.id == company_id
        ).all()

        df_pg = pd.DataFrame(sql_query)
        area_list = df_pg['areaid'].to_list()

        pipeline = [
            {"$match": {"area_id": {"$in": area_list}}},
            {
                "$project": {
                    "_id": 0,
                    "area_name": 0,
                }
            }
        ]

        df_mg = pd.DataFrame(list(mongo.db.api.aggregate(pipeline)))
        df_merged = pd.merge(df_pg, df_mg, left_on='areaid', right_on='area_id', how='inner')
        df_merged.drop(columns=['area_id', 'areaid'], inplace=True)
        
        return df_merged.to_dict(orient='records')

    except KeyError as error:
        print(error)
        abort(400, description=Messages.ERROR_INVALID_DATA('Area Information'))
    except Exception as error:
        print(error)
        abort(500, description=Messages.UNKNOWN_ERROR('Area Information'))
