from flask import Blueprint, abort, request, jsonify
from flasgger import swag_from

from datetime import datetime

from app.database import db
from app.models import Area, Localization
from app.util.messages import Messages
from app.initializer import app, mongo

area_information = Blueprint(
    "area_information", __name__, url_prefix=app.config["API_URL_PREFIX"] + "/area-information"
)

@area_information.route("/", methods=["GET"])
# @jwt_required()
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
        area_id = params.get('area_id', False)
        start_date = params.get('start_date', '2000-01-01')
        end_date = params.get('end_date', str(datetime.now().strftime('%Y-%m-%d')))

        if area_id:
            filters['area_id'] = int(area_id)

        if start_date or end_date:
            filters['measurement_date'] = {
                "$gte": datetime.strptime(start_date, "%Y-%m-%d"),
                "$lt": datetime.strptime(end_date, "%Y-%m-%d")
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
# @jwt_required()
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
    data = request.json
    if not data:
        abort(400, description=Messages.ERROR_INVALID_DATA('Area Information'))

    mongo.db.api.insert_one(data)
    return jsonify({"msg": Messages.SUCCESS_SAVE_SUCCESSFULLY('Area Information')})


@area_information.route("/tree", methods=["GET"])
# @jwt_required()
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
        start_date = params.get('start_date', '2000-01-01')
        end_date = params.get('end_date', str(datetime.now().strftime('%Y-%m-%d')))

        if area_id:
            filters['area_id'] = int(area_id)

        if start_date or end_date:
            filters['measurement_date'] = {
                "$gte": datetime.strptime(start_date, "%Y-%m-%d"),
                "$lt": datetime.strptime(end_date, "%Y-%m-%d"),
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
# @jwt_required()
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
        start_date = params.get('start_date', '2000-01-01')
        end_date = params.get('end_date', str(datetime.now().strftime('%Y-%m-%d')))

        if area_id:
            filters['area_id'] = int(area_id)

        if start_date or end_date:
            filters['measurement_date'] = {
                "$gte": datetime.strptime(start_date, "%Y-%m-%d"),
                "$lt": datetime.strptime(end_date, "%Y-%m-%d"),
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
