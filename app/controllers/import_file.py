from datetime import datetime

from flasgger import swag_from
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
import pandas as pd
from app.database import db
from app.models import Area, Localization, Company
from app.initializer import app, mongo


files = Blueprint("files", __name__, url_prefix=app.config["API_URL_PREFIX"] + "/import")


@files.route("/csv_sql", methods=["POST"])
@swag_from({
    'tags': ['Import CSV'],
    'summary': 'Import data to POSTGRES database',
    'description': 'Import all structured data from a CSV file and fill the database with this information.',
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'CSV file containing data to import'
        }
    ],
    'responses': {
        '200': {
            'description': 'Data successfully imported',
        },
        '400': {
            'description': 'Bad request, file not found or invalid format',
        },
        '500': {
            'description': 'Server error while processing the file',
        }
    }
})
def import_csv_sql():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    if not filename.endswith(".csv"):
        return jsonify({"error": "Invalid file format, only .csv allowed"}), 400

    try:
        df = pd.read_csv(file, decimal=",")

        required_columns = [
            "area_name", "number_of_trees_planted", "planting_techniques", "total_area_hectares",
            "reflorested_area_hectares", "planted_species", "initial_planted_area_hectares",
            "initial_vegetation_cover", "company_name", "cnpj", "uf", "city", "altitude", "soil_type"
        ]

        if not all(col in df.columns for col in required_columns):
            return jsonify({"error": "Missing required columns in file"}), 400

        areas = []

        for _, row in df.iterrows():
            localization = Localization.query.filter_by(
                uf=row["uf"], city=row["city"]
            ).first()

            if not localization:
                localization = Localization(
                    uf=row["uf"],
                    city=row["city"],
                    altitude=float(row["altitude"]),
                    soil_type=row["soil_type"]
                )
                db.session.add(localization)
                db.session.flush()

            company = Company.query.filter_by(cnpj=str(row["cnpj"])).first()

            if not company:
                company = Company(
                    cnpj=str(row["cnpj"]),
                    name=row["company_name"]
                )
                db.session.add(company)
                db.session.flush()

            area = Area(
                area_name=row["area_name"],
                number_of_trees_planted=int(row["number_of_trees_planted"]),
                planting_techniques=row["planting_techniques"],
                total_area_hectares=float(row["total_area_hectares"]),
                reflorested_area_hectares=float(row["reflorested_area_hectares"]),
                planted_species=row["planted_species"],
                initial_planted_area_hectares=row["initial_planted_area_hectares"],
                initial_vegetation_cover=row["initial_vegetation_cover"],
                localization_id=localization.id,
                company_id=company.id
            )

            areas.append(area)

        db.session.bulk_save_objects(areas)
        db.session.commit()
        return jsonify({"message": "Data imported successfully"}), 201

    except (ValueError, SQLAlchemyError) as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@files.route("/csv_nosql", methods=["POST"])
@swag_from({
    'tags': ['Import CSV'],
    'summary': 'Import noSql data to Mongo database',
    'description': 'Import all nosql data from a CSV file and fill the database with this information.',
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'CSV file containing data to import'
        }
    ],
    'responses': {
        '200': {
            'description': 'Data successfully imported',
        },
        '400': {
            'description': 'Bad request, file not found or invalid format',
        },
        '500': {
            'description': 'Server error while processing the file',
        }
    }
})

def import_csv_nosql():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    if not filename.endswith(".csv"):
        return jsonify({"error": "Invalid file format, only .csv allowed"}), 400

    try:
        df = pd.read_csv(file, decimal=",")

        required_columns = [
            "soil_fertility_index_percent", "area_code", "area_name",
            "avoided_co2_emissions_cubic_meters", "number_of_trees_lost", "tree_health_status",
            "average_tree_growth_cm", "water_sources", "water_quality_indicators",
            "pest_management", "fertilization", "irrigation", "environmental_threats",
            "total_project_cost_brl", "funding_source", "stage_indicator", "measurement_date",
            "living_trees_to_date", "tree_survival_rate"
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return jsonify({"error": f"Missing required columns in file - missing_columns: {missing_columns}"}), 400

        for _, row in df.iterrows():
            area = Area.query.filter_by(area_name=row["area_name"]).first()
            if area is not None:
                area_measurements = {
                    "area_id": area.id,
                    "soil_fertility_index_percent": row["soil_fertility_index_percent"],
                    "area_code": row["area_code"],
                    "area_name": row["area_name"],
                    "avoided_co2_emissions_cubic_meters": float(row["avoided_co2_emissions_cubic_meters"]),
                    "number_of_trees_lost": int(row["number_of_trees_lost"]),
                    "tree_health_status": row["tree_health_status"],
                    "average_tree_growth_cm": float(row["average_tree_growth_cm"]),
                    "water_sources": row["water_sources"],
                    "water_quality_indicators": row["water_quality_indicators"],
                    "pest_management": row["pest_management"],
                    "fertilization": row["fertilization"],
                    "irrigation": row["irrigation"],
                    "environmental_threats": row["environmental_threats"],
                    "total_project_cost_brl": float(row["total_project_cost_brl"]),
                    "funding_source": row["funding_source"],
                    "stage_indicator": row["stage_indicator"],
                    "measurement_date": datetime.strptime(row["measurement_date"], "%Y-%m-%d"),
                    "living_trees_to_date": int(row["living_trees_to_date"]),
                    "tree_survival_rate": float(row["tree_survival_rate"]),
                }

                mongo.db.api.insert_one(area_measurements)

        return jsonify({"message": "Data imported successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500