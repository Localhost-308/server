import os
import base64
import pandas as pd
from sqlalchemy import func
from flasgger import swag_from
from flask import Blueprint, abort, send_file
from flask_jwt_extended import jwt_required, get_jwt

from app.database import db
from app.util.pdf import MarkdownToPDF
from app.util.messages import Messages
from app.initializer import app, mongo#, chat
from app.util.graph_builder import GraphBuilder
from app.models import Area, Company, Localization
from app.util.report_messages import graph_analysis

report = Blueprint("report", __name__, url_prefix=app.config["API_URL_PREFIX"] + "/report")

@report.route("/", methods=["GET"])
@jwt_required()
def get_report():
    try:
        pdf = MarkdownToPDF()
        claims = get_jwt()
        company_id = claims.get('company_id')
        columns = [
            "area_name",
            # "uf",
            # "city",
            "planting_techniques",
            "planted_species",
            "total_area_hectares",
            "initial_planted_area_hectares",
            "initial_vegetation_cover",
            "soil_fertility_index_percent",
            "avoided_co2_emissions_cubic_meters",
            "number_of_trees_lost",
            "tree_health_status",
            "average_tree_growth_cm",
            "water_sources",
            "water_quality_indicators",
            "pest_management",
            "fertilization",
            "irrigation",
            "environmental_threats",
            # "total_project_cost_brl",
            # "funding_source",
            "stage_indicator",
            "measurement_date",
            "living_trees_to_date",
            "tree_survival_rate"
        ]

        sql_query = db.session.query(
            (Area.id).label('areaid'), Area.area_name, Area.planting_techniques, Area.planted_species, 
            Area.total_area_hectares, Area.initial_planted_area_hectares, Area.initial_vegetation_cover,
            Localization.uf, Localization.city
        ).join(Company).join(Localization).filter(
            Company.id == 1
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
        df_merged = df_merged[columns]
        df_merged["measurement_date"] = pd.to_datetime(df_merged["measurement_date"]).dt.strftime("%Y-%m-%d")

        graph = GraphBuilder()
        temp_file_path = os.getenv('TEMPORARY_FOLDER_PATH')
        path_image_1 = f'{temp_file_path}/image/image_1.png'
        path_image_2 = f'{temp_file_path}/image/image_2.png'
        data = df_merged.to_dict(orient='records')
        graph.plot_trend_analysis(data, path_image_1)
        graph.plot_area_evolution(data, path_image_2)

        message = f"dados: A seguinte lista de dados deve ser usada para gerar os relatórios:\n{df_merged.to_dict(orient='records')}"
        # pdf.add_page(chat.send_message(message))
        
        with open(path_image_1, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
            base64_image_1 = f"data:image/png;base64,{encoded}"
        with open(path_image_2, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
            base64_image_2 =  f"data:image/png;base64,{encoded}"

        graph_analysis_formatted= graph_analysis.replace('<<path_image_1>>', base64_image_1)
        graph_analysis_formatted = graph_analysis_formatted.replace('<<path_image_2>>', base64_image_2)
        pdf.add_page(graph_analysis_formatted)
        pdf.save()

        return send_file(pdf.get_path(), download_name='relatorio.pdf', mimetype='application/pdf', as_attachment=True)
    except Exception as error:
        print('ERRO: ', error)
        abort(500, description=Messages.UNKNOWN_ERROR('Report'))
