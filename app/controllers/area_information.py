import pandas as pd
from flask import Blueprint, abort, request, jsonify
from flasgger import swag_from
from flask_jwt_extended import jwt_required

from datetime import datetime

from sqlalchemy import func

from app.database import db
from app.models import Area, Localization
from app.util.messages import Messages
from app.initializer import app, mongo
from app.util.utils import convert_dict_keys_to_camel_case


area_information = Blueprint(
    "area_information", __name__, url_prefix=app.config["API_URL_PREFIX"] + "/area-information"
)


@area_information.route("/", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Area Information'],
    'summary': 'Get filtered area information',
    'description': 'Retrieve area information based on optional filters like area_id and date range.',
    'parameters': [
        {
            'name': 'area_id',
            'in': 'query',
            'required': False,
            'schema': {'type': 'integer'},
            'description': 'The ID of the area'
        },
        {
            'name': 'start_date',
            'in': 'query',
            'required': False,
            'schema': {'type': 'string', 'format': 'date'},
            'description': 'Start date for filtering (YYYY-MM-DD)'
        },
        {
            'name': 'end_date',
            'in': 'query',
            'required': False,
            'schema': {'type': 'string', 'format': 'date'},
            'description': 'End date for filtering (YYYY-MM-DD)'
        }
    ],
    'responses': {
        200: {
            'description': 'Aggregated area information based on the provided filters',
            'content': {
                'application/json': {
                    'example': [
                        {
                            "measurement_date": "2024-02",
                            "total_avoided_co2": 1500.5
                        }
                    ]
                }
            }
        },
        400: {
            'description': Messages.ERROR_INVALID_DATA('Area Information')
        },
        500: {
            'description': Messages.UNKNOWN_ERROR('Area Information')
        }
    }
})
def get_all_by():
    try:
        filters = {}
        params = request.args
        area_id = params.get('area_id', None)
        start_date = datetime.strptime(params.get('start_date', '2000-01-01'), "%Y-%m-%d")
        end_date = datetime.strptime(params.get('end_date', datetime.now().strftime('%Y-%m-%d')), "%Y-%m-%d")

        if area_id:
            filters['area_id'] = int(area_id)

        filters['measurement_date'] = {
            "$gte": start_date,
            "$lt": end_date
        }

        pipeline = [
            {"$match": filters},
            {
                "$group": {
                    "_id": {"$substr": ["$measurement_date", 0, 7]},
                    "total_avoided_co2": {"$sum": "$avoided_co2_emissions_cubic_meters"}
                }
            },
            {"$sort": {"_id": 1}},
            {"$project": {"_id": 0, "measurement_date": "$_id", "total_avoided_co2": 1}}
        ]

        area_info = list(mongo.db.api.aggregate(pipeline))
        return jsonify(area_info)

    except KeyError as error:
        abort(400, description=Messages.ERROR_INVALID_DATA('Area Information'))
    except Exception as error:
        abort(500, description=Messages.UNKNOWN_ERROR('Area Information'))


@area_information.route("/", methods=["POST"])
@jwt_required()
@swag_from({
    'tags': ['Area Information'],
    'summary': 'Create a new area information entry',
    'description': 'Add a new area information record to the database.',
    'responses': {
        201: {'description': 'Area information created successfully'},
        400: {'description': Messages.ERROR_INVALID_DATA('Area Information')}
    }
})
def save_area_information():
    try:
        data = request.json
        if not data:
            abort(400)
        
        data['measurement_date'] = datetime.strptime(data["measurement_date"], "%Y-%m-%d")
        mongo.db.api.insert_one(data)
        return jsonify({"msg": Messages.SUCCESS_SAVE_SUCCESSFULLY('Area Information')})
    
    except KeyError as error:
        abort(400, description=Messages.ERROR_INVALID_DATA('Area Information'))
    except Exception as error:
        abort(500, description=Messages.UNKNOWN_ERROR('Area Information'))


@area_information.route("/tree", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Area Information'],
    'summary': 'Retrieve area information on tree measurements',
    'description': 'Fetches aggregated data on tree measurements (such as number of trees lost, growth, etc.) for a given area and date range.',
    'parameters': [
        {
            'name': 'area_id',
            'in': 'query',
            'type': 'integer',
            'description': 'ID of the area to filter the data by.',
            'required': False
        },
        {
            'name': 'start_date',
            'in': 'query',
            'type': 'string',
            'format': 'date',
            'description': 'Start date of the date range to filter the data (YYYY-MM-DD). Default is 2000-01-01.',
            'required': False
        },
        {
            'name': 'end_date',
            'in': 'query',
            'type': 'string',
            'format': 'date',
            'description': 'End date of the date range to filter the data (YYYY-MM-DD). Default is the current date.',
            'required': False
        }
    ],
    'responses': {
        200: {
            'description': 'Aggregated tree information successfully retrieved.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'measurement_date': {'type': 'string', 'example': '2025-03-19'},
                        'total_number_of_trees_lost': {'type': 'integer', 'example': 12042},
                        'total_average_tree_growth_cm': {'type': 'number', 'example': 164.3},
                        'total_trees_alive_so_far': {'type': 'integer', 'example': 54884},
                        'total_tree_survival_rate': {'type': 'number', 'example': 82.00}
                    }
                }
            }
        },
        400: {
            'description': 'Invalid input data. Ensure the area ID and dates are correct.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': Messages.ERROR_INVALID_DATA('Area Information')}
                }
            }
        },
        500: {
            'description': 'Internal server error occurred.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': Messages.UNKNOWN_ERROR('Area Information')}
                }
            }
        }
    }
})
def get_tree_information():
    try:
        filters = {}
        params = request.args
        area_id = params.get('area_id', False)
        start_date = datetime.strptime(params.get('start_date', '2000-01-01'), "%Y-%m-%d")
        end_date = datetime.strptime(params.get('end_date', datetime.now().strftime('%Y-%m-%d')), "%Y-%m-%d")

        if area_id:
            filters['area_id'] = int(area_id)

        filters['measurement_date'] = {
            "$gte": start_date,
            "$lt": end_date
        }

        pipeline = [
            {"$match": filters},
            {
                "$group": {
                    "_id": {"$substr": ["$measurement_date", 0, 7]},
                    "total_number_of_trees_lost": {"$sum": "$number_of_trees_lost"},
                    "total_living_trees_to_date": {"$sum": "$living_trees_to_date"}
                }
            },
            {"$sort": {"_id": 1}},
            {"$project": {
                "_id": 0,
                "measurement_date": "$_id",
                "total_number_of_trees_lost": 1,
                "total_living_trees_to_date": 1,
                "survival_rate": {
                    "$round": [
                        {
                            "$cond": {
                                "if": {
                                    "$eq": [
                                        {"$add": ["$total_number_of_trees_lost", "$total_living_trees_to_date"]}, 0
                                    ]
                                },
                                "then": 0,
                                "else": {
                                    "$divide": [
                                        "$total_living_trees_to_date",
                                        {
                                            "$add": ["$total_number_of_trees_lost", "$total_living_trees_to_date"]
                                        }
                                    ]
                                }
                            }
                        },
                        4
                    ]
                }
            }}
        ]

        tree_info = list(mongo.db.api.aggregate(pipeline))
        return jsonify(tree_info)

    except KeyError as error:
        abort(400, description=Messages.ERROR_INVALID_DATA('Area Information'))
    except Exception as error:
        abort(500, description=Messages.UNKNOWN_ERROR('Area Information'))


@area_information.route("/soil", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Area Information'],
    'summary': 'Retrieve aggregated soil fertility index by month and year',
    'description': 'Fetches aggregated data for soil fertility index, calculated as the average percentage, for a given area and date range.',
    'parameters': [
        {
            'name': 'area_id',
            'in': 'query',
            'type': 'integer',
            'description': 'ID of the area to filter the data by.',
            'required': False
        },
        {
            'name': 'start_date',
            'in': 'query',
            'type': 'string',
            'format': 'date',
            'description': 'Start date of the date range to filter the data (YYYY-MM-DD). Default is 2000-01-01.',
            'required': False
        },
        {
            'name': 'end_date',
            'in': 'query',
            'type': 'string',
            'format': 'date',
            'description': 'End date of the date range to filter the data (YYYY-MM-DD). Default is the current date.',
            'required': False
        }
    ],
    'responses': {
        200: {
            'description': 'Aggregated soil fertility index successfully retrieved.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'measurement_date': {'type': 'string', 'example': '2025-03'},
                        'fertilization': {'type': 'string', 'example': 'Orgânica'},
                        'avg_soil_fertility_index_percent': {'type': 'number', 'example': 0.7502}
                    }
                }
            }
        },
        400: {
            'description': 'Invalid input data. Ensure the area ID and dates are correct.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': Messages.ERROR_INVALID_DATA('Area Information')}
                }
            }
        },
        500: {
            'description': 'Internal server error occurred.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': Messages.UNKNOWN_ERROR('Area Information')}
                }
            }
        }
    }
})
def get_soil_information():
    try:
        filters = {}
        params = request.args
        area_id = params.get('area_id', False)
        start_date = datetime.strptime(params.get('start_date', '2000-01-01'), "%Y-%m-%d")
        end_date = datetime.strptime(params.get('end_date', datetime.now().strftime('%Y-%m-%d')), "%Y-%m-%d")

        if area_id:
            filters['area_id'] = int(area_id)

        filters['measurement_date'] = {
            "$gte": start_date,
            "$lt": end_date
        }

        pipeline = [
            {"$match": filters},
            {
                "$group": {
                    "_id": {
                        "measurement_date": {"$substr": ["$measurement_date", 0, 7]},
                        "fertilization": "$fertilization"
                    },
                    "avg_soil_fertility_index_percent": {"$avg": "$soil_fertility_index_percent"}
                }
            },
            {"$sort": {"_id.measurement_date": 1, "_id.fertilization": 1}},
            {
                "$project": {
                    "_id": 0,
                    "measurement_date": "$_id.measurement_date",
                    "fertilization": "$_id.fertilization",
                    "avg_soil_fertility_index_percent": {
                        "$round": ["$avg_soil_fertility_index_percent", 2]
                    }
                }
            }
        ]

        area_info = list(mongo.db.api.aggregate(pipeline))
        return jsonify(area_info)
    except KeyError as error:
        abort(400, description=Messages.ERROR_INVALID_DATA('Area Information'))
    except Exception as error:
        abort(500, description=Messages.UNKNOWN_ERROR('Area Information'))


@area_information.route("/total-planted-trees", methods=["GET"])
@jwt_required()
@swag_from({
    "tags": ["Area Information"],
    "summary": "Total de árvores plantadas ",
    "description": "Retorna o total de árvores plantadas filtrando por estado (UF) e/ou tipo de espécies.",
    "parameters": [
        {
            "name": "uf",
            "in": "query",
            "type": "string",
            "required": False,
            "description": "Filtrar por estado (UF) das áreas.",
            "example": "SP"
        },
        {
            "name": "species",
            "in": "query",
            "type": "string",
            "required": False,
            "enum": ["Espécies Exóticas", "Espécies Nativas", "Espécies Misturadas"],
            "description": "Filtrar pelo tipo de espécie plantada.",
            "example": "Espécies Nativas"
        },
        {
            "name": "start_date",
            "in": "query",
            "type": "string",
            "required": False,
            "description": "Data inicial para considerar medições.",
            "example": "2024-01-01"
        },
        {
            "name": "end_date",
            "in": "query",
            "type": "string",
            "required": False,
            "description": "Data final para considerar medições.",
            "example": "2024-12-31"
        }
    ],
    "responses": {
        "200": {
            "description": "Total de árvores plantadas.",
            "schema": {
                "type": "object",
                "properties": {
                    "total_planted_trees": {
                        "type": "integer",
                        "example": 12000
                    }
                }
            }
        },
        "400": {
            "description": "Erro nos parâmetros da requisição."
        },
        "500": {
            "description": "Erro interno do servidor."
        }
    }
})
def get_total_planted_trees():
    try:
        uf = request.args.get("uf")
        species = request.args.get("species")
        start_date = request.args.get("start_date", "2000-01-01")
        end_date = request.args.get("end_date", str(datetime.now().strftime("%Y-%m-%d")))

        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")

        sql_query = db.session.query(
            Area.id, Area.number_of_trees_planted
        ).join(Localization).filter(
            (Localization.uf == uf.upper()) if uf else True,
            (Area.planted_species.ilike(f"%{species}%")) if species else True
        ).all()

        area_ids = {area.id: area.number_of_trees_planted for area in sql_query}

        if not area_ids:
            return jsonify({"total_trees": 0})

        pipeline = [
            {"$match": {
                "area_id": {"$in": list(area_ids.keys())},
                "measurement_date": {"$gte": start_date_dt, "$lte": end_date_dt}
            }},
            {"$sort": {"measurement_date": 1}},
            {"$group": {
                "_id": "$area_id",
                "first_measurement": {"$first": "$measurement_date"}
            }}
        ]

        first_measurements = list(mongo.db.api.aggregate(pipeline))

        valid_area_ids = {entry["_id"] for entry in first_measurements}

        total_trees = sum(area_ids[area_id] for area_id in valid_area_ids)

        return jsonify({"total_planted_trees": total_trees})

    except Exception as error:
        abort(500, description=str(error))


@swag_from({
    "summary": "Obter sumário de reflorestamento por UF/Tipo de solo/Tecnica de plantio",
    "description": "Retorna a soma da área reflorestada agrupada por estado (UF), tipo de solo e técnica de plantio.",
    "responses": {
        200: {
            "description": "Retorna um JSON com os totais de área reflorestada por estado.",
            "content": {
                "application/json": {
                    "example": {
                        "sp": {
                            "total": 123412341234,
                            "soil_type": {
                                "total": 100,
                                "pedregoso": 50,
                                "argiloso": 50
                            },
                            "planting_techniques": {
                                "total": 100,
                                "foo": 30,
                                "bar": 70
                            }
                        },
                        "mg": {
                            "total": 200,
                            "soil_type": {
                                "total": 200,
                                "arenoso": 80,
                                "humoso": 120
                            },
                            "planting_techniques": {
                                "total": 200,
                                "hidroponia": 90,
                                "orgânico": 110
                            }
                        }
                    }
                }
            }
        }
    },
    "tags": ["Area Information"]
})
@area_information.route("/reforested-area-summary", methods=["GET"])
@jwt_required()
def get_reforested_area_summary():
    query = (
        db.session.query(
            Localization.uf,
            Localization.soil_type,
            Area.planting_techniques,
            func.sum(Area.reflorested_area_hectares).label("total_area")
        )
        .join(Localization, Area.localization_id == Localization.id)
        .group_by(Localization.uf, Localization.soil_type, Area.planting_techniques)
        .all()
    )

    df = pd.DataFrame(query, columns=["uf", "soil_type", "planting_techniques", "total_area"])

    if df.empty:
        return jsonify({})

    df["uf"] = df["uf"].str.lower()

    total_by_uf = df.groupby("uf")["total_area"].sum().to_dict()

    total_by_soil = df.groupby(["uf", "soil_type"])["total_area"].sum().unstack(fill_value=0)
    total_by_soil["total"] = total_by_soil.sum(axis=1)
    total_by_soil = total_by_soil.to_dict(orient="index")

    total_by_technique = df.groupby(["uf", "planting_techniques"])["total_area"].sum().unstack(fill_value=0)
    total_by_technique["total"] = total_by_technique.sum(axis=1)
    total_by_technique = total_by_technique.to_dict(orient="index")

    result = {
        uf: {
            "total": total_by_uf[uf],
            "soil_type": total_by_soil.get(uf, {"total": 0}),
            "planting_techniques": total_by_technique.get(uf, {"total": 0})
        }
        for uf in total_by_uf
    }

    return jsonify(result)


@swag_from({
    "tags": ["Area Information"],
    "summary": "Obter total de custos de projetos por fonte de financiamento",
    "description": "Retorna o total de custos de projetos (`total_project_cost_brl`) agrupados por fonte de financiamento (`funding_source`)."
                   "Os resultados podem ser filtrados por estado (`uf`) e ano (`year`). Se nenhum parâmetro for passado, retorna os valores totais.",
    "parameters": [
        {
            "name": "uf",
            "in": "query",
            "type": "string",
            "required": False,
            "description": "Sigla do estado (UF) para filtrar os resultados."
        },
        {
            "name": "year",
            "in": "query",
            "type": "integer",
            "required": False,
            "description": "Ano para filtrar os dados."
        }
    ],
    "responses": {
        200: {
            "description": "Resposta com os valores totais e percentuais por fonte de financiamento.",
            "examples": {
                "application/json": {
                    "uf": "sp",
                    "year": 2024,
                    "total": 200000.0,
                    "funding_sources": {
                        "Governo": {"total": 100000.0, "percent": 50.0},
                        "ONG": {"total": 60000.0, "percent": 30.0},
                        "Privado": {"total": 40000.0, "percent": 20.0}
                    }
                }
            }
        },
        404: {
            "description": "Nenhum dado encontrado para os filtros fornecidos."
        }
    }
})
@area_information.route("/funding_by_uf_year", methods=["GET"])
@jwt_required()
def get_funding_by_uf_year():
    uf = request.args.get("uf", type=str)
    year = request.args.get("year", type=int)

    mongo_query = {}
    if year:
        mongo_query["measurement_date"] = {
            "$gte": datetime(year, 1, 1),
            "$lt": datetime(year + 1, 1, 1),
        }
    mongo_data = list(mongo.db.api.find(mongo_query, {"area_id": 1, "funding_source": 1, "total_project_cost_brl": 1, "_id": 0}))

    if not mongo_data:
        return jsonify({"error": "Nenhum dado encontrado para os filtros fornecidos."}), 404

    df = pd.DataFrame(mongo_data)

    if uf:
        areas = db.session.query(Area.id, Localization.uf).join(Localization, Area.localization_id == Localization.id).all()
        area_uf_map = {area.id: area.uf.lower() for area in areas}
        df["uf"] = df["area_id"].map(area_uf_map)

        df = df[df["uf"] == uf.lower()]

    funding_totals = df.groupby("funding_source")["total_project_cost_brl"].sum()

    total = funding_totals.sum()
    funding_percentages = (funding_totals / total * 100).round(2)

    result = {
        "uf": uf.lower() if uf else "all",
        "year": year if year else "all",
        "total": total,
        "funding_sources": {
            source.lower().replace(" ", "_"): {"total": float(value), "percent": float(funding_percentages[source])}
            for source, value in funding_totals.items()
        }
    }

    return jsonify(result)


@swag_from({
    'tags': ['Area Information'],
    'description': 'Saúde das árvores agrupadas por técnicas de plantio.',
    'responses': {
        200: {
            'description': 'Dados de saúde das árvores por técnica de plantio.'
        },
        500: {
            'description': 'Erro ao processar os dados.'
        }
    }
})
@area_information.route("/tree-health", methods=["GET"])
@jwt_required()
def get_area_tree_health():
    query = db.session.query(
        Area.id,
        Area.planting_techniques,
        Area.number_of_trees_planted
    ).all()

    df_sql = pd.DataFrame(query, columns=["area_id", "planting_techniques", "trees_planted"])

    mongo_data = mongo.db.api.aggregate([
        {"$sort": {"measurement_date": -1}},
        {"$group": {"_id": "$area_id", "tree_health_status": {"$first": "$tree_health_status"}}}
    ])
    df_mongo = pd.DataFrame(mongo_data)
    df_mongo.rename(columns={"_id": "area_id"}, inplace=True)

    df_merged = df_sql.merge(df_mongo, on="area_id", how="left")

    df_result = df_merged.groupby(
        ["planting_techniques", "tree_health_status"]
    )["trees_planted"].sum().unstack().fillna(0).astype(int)

    result = df_result.to_dict(orient="index")
    result = convert_dict_keys_to_camel_case(result)
    return jsonify(result)


@area_information.route("/tree/status", methods=["GET"])
@jwt_required()
def get_tree_status():
    try:
        filters = {}
        params = request.args
        area_id = params.get('area_id', default=None, type=int)
        start_date = datetime.strptime(params.get('start_date', default='2000-01-01', type=str), "%Y-%m-%d")
        end_date = datetime.strptime(params.get('end_date', default=datetime.now().strftime('%Y-%m-%d'), type=str), "%Y-%m-%d")
        uf = params.get('uf', default=None, type=str)

        if area_id:
            filters['area_id'] = int(area_id)

        filters['measurement_date'] = {
            "$gte": start_date,
            "$lt": end_date
        }

        sql_query = db.session.query(
            Area.id, Area.area_name
        ).join(Localization).filter(
            (Area.id == area_id) if area_id else True,
            (Localization.uf == uf.upper()) if uf else True,
        ).all()

        pipeline = [
            {"$match": filters},
            {
                "$group": {
                    "_id": {
                        "measurement_date": {"$substr": ["$measurement_date", 0, 7]},
                    },
                    "area_id": {"$first": "$area_id"},
                    "tree_health_status": {"$first": "$tree_health_status"}
                }
            },
            {"$sort": {"_id.measurement_date": 1, "_id.fertilization": 1}},
            {
                "$project": {
                    "_id": 0,
                    "measurement_date": "$_id.measurement_date",
                    "area_id": "$area_id",
                    "tree_health_status": "$tree_health_status"
                }
            }
        ]

        df_pg = pd.DataFrame(sql_query)
        df_mg = pd.DataFrame(list(mongo.db.api.aggregate(pipeline)))
        df_merged = pd.merge(df_pg, df_mg, left_on='id', right_on='area_id', how='inner')
        df_merged.drop(columns=['area_id', 'id'], inplace=True)

        return jsonify(df_merged.to_dict(orient='records'))

    except KeyError as error:
        print(error)
        abort(400, description=Messages.ERROR_INVALID_DATA('Area Information'))
    except Exception as error:
        print(error)
        abort(500, description=Messages.UNKNOWN_ERROR('Area Information'))
