from flasgger import swag_from
from flask import Blueprint
from app.initializer import app


files = Blueprint("files", __name__, url_prefix=app.config["API_URL_PREFIX"] + "/import")
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
import pandas as pd
from app.database import db
from app.models import Area, Localization, Company
from app.initializer import app


files = Blueprint("files", __name__, url_prefix=app.config["API_URL_PREFIX"] + "/import")


@files.route("/csv", methods=["POST"])
@swag_from({
    'tags': ['Import CSV'],
    'summary': 'Import data from CSV file',
    'description': 'Import all data from a CSV file and fill the database with this information.',
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
def import_csv():
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
