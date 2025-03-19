from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from app.database import db
from app.models import Area, Localization
from app.initializer import app


files = Blueprint("files", __name__, url_prefix=app.config["API_URL_PREFIX"] + "/xls")

@files.route("/xls", methods=["POST"])
def import_xls():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    if not filename.endswith(".xls"):
        return jsonify({"error": "Invalid file format, only .xls allowed"}), 400

    try:
        df = pd.read_excel(file)

        required_columns = [
            "number_of_trees_planted", "planting_techniques", "reflorested_area",
            "planted_species", "total_planted_area", "initial_vegetation_cover",
            "localization_id", "company_id", "uf", "city", "altitude", "soil_type"
        ]

        if not all(col in df.columns for col in required_columns):
            return jsonify({"error": "Missing required columns in file"}), 400

        areas = []
        localizations = {}
        for _, row in df.iterrows():
            loc_id = int(row["localization_id"])
            if loc_id not in localizations:
                localizations[loc_id] = Localization(
                    id=loc_id,
                    uf=row["uf"],
                    city=row["city"],
                    altitude=float(row["altitude"]),
                    soil_type=row["soil_type"]
                )

            area = Area(
                number_of_trees_planted=int(row["number_of_trees_planted"]),
                planting_techniques=row["planting_techniques"],
                reflorested_area=float(row["reflorested_area"]),
                planted_species=row["planted_species"],
                total_planted_area=float(row["total_planted_area"]),
                initial_vegetation_cover=row["initial_vegetation_cover"],
                localization_id=loc_id,
                company_id=int(row["company_id"])
            )
            areas.append(area)

        db.session.bulk_save_objects(localizations.values())
        db.session.bulk_save_objects(areas)
        db.session.commit()
        return jsonify({"message": "Data imported successfully"}), 201

    except (ValueError, SQLAlchemyError) as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
