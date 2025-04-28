from flask import Blueprint, abort, request
from flask_jwt_extended import jwt_required
import joblib
import pandas as pd
from datetime import datetime
from mlxtend.frequent_patterns import apriori, association_rules

from app.initializer import app, mongo
from app.database import db

machine_learning = Blueprint(
    "machine_learning",
    __name__,
    url_prefix=app.config["API_URL_PREFIX"] + "/machine_learning",
)

MODEL = joblib.load('model_v2.pkl')
SCALER = joblib.load('scaler_v2.pkl')
COLUMNS_USED = joblib.load('columns_used.pkl')

@machine_learning.route("/predict-tree-health", methods=["POST"])
# @jwt_required()
def predict_tree_health():
    try:
        data = request.get_json()

        input_data = {
            'number_of_trees_lost': data.get('number_of_trees_lost', 0),
            'avoided_co2_emissions_cubic_meters': data.get('avoided_co2_emissions_cubic_meters', 0),
            'average_tree_growth_cm': data.get('average_tree_growth_cm', 0),
            'water_sources': data['water_sources'],
            'pest_management': data['pest_management'],
            'fertilization': data['fertilization'],
            'irrigation': data['irrigation'],
            'environmental_threats': data['environmental_threats'],
            'total_project_cost_brl': data.get('total_project_cost_brl', 0),
            'stage_indicator': data['stage_indicator'],
            'living_trees_to_date': data.get('living_trees_to_date', 0),
            'soil_fertility_index_percent': data.get('soil_fertility_index_percent', 0),
            'water_quality_indicators': data['water_quality_indicators']
        }
        df = pd.DataFrame([input_data])
        df_encoded = pd.get_dummies(df, columns=[
            'water_sources', 
            'pest_management', 
            'fertilization', 
            'irrigation', 
            'environmental_threats',
            'stage_indicator',
            'water_quality_indicators'
        ])
        for col in COLUMNS_USED:
            if col not in df_encoded.columns:
                df_encoded[col] = 0

        df_encoded = df_encoded[COLUMNS_USED]
        input_scaled = SCALER.transform(df_encoded)
        prediction = MODEL.predict(input_scaled)
        return {'prediction': prediction[0]}

    except KeyError as e:
        return abort(400, description=f"Missing parameter: {str(e)}")
    except Exception as e:
        return abort(500, description=f"error: {str(e)}")
    

@machine_learning.route("/association-rules", methods=["GET"])
# @jwt_required()
def generate_association_rules():
    try:
        area_info = list(mongo.db.api.find({}))
        
        if not area_info:
            return abort(404, description="No data found")

        df = pd.DataFrame(area_info)
        df['high_survival'] = df['tree_survival_rate'] > 70
        high_survival_practices = df[df['high_survival']][
            ['water_sources', 'pest_management', 'fertilization', 'irrigation', 'environmental_threats']
        ]
        practices_dummies = pd.get_dummies(high_survival_practices)

        frequent_itemsets = apriori(practices_dummies, min_support=0.05, use_colnames=True)
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)

        def split_feature(feature):
            parts = feature.split('_')
            col_name = '_'.join(parts[:-1])
            value = parts[-1]
            return col_name, value
        
        formatted_rules = []
        for _, rule in rules.iterrows():
            conseq_item = list(rule['consequents'])[0]
            conseq_col, conseq_value = split_feature(conseq_item)
            formatted_rule = {
                "antecedents": list(rule['antecedents'])[0].split('_', 1)[1],
                "confidence": rule['confidence'],
                "consequents": {
                    conseq_col: conseq_value
                },
                "lift": rule['lift'],
                "support": rule['support']
            }
            formatted_rules.append(formatted_rule)

        return formatted_rules

    except Exception as e:
        return abort(500, description=f"error: {str(e)}")

@machine_learning.route("/list", methods=["GET"])
def get_valores_unicos():
    collection = mongo.db.api
    return {
        # 'number_of_trees_lost': collection.distinct('number_of_trees_lost'),
        # 'avoided_co2_emissions_cubic_meters': collection.distinct('avoided_co2_emissions_cubic_meters'),
        # 'average_tree_growth_cm': collection.distinct('average_tree_growth_cm'),
        'water_sources': collection.distinct('water_sources'),
        'pest_management': collection.distinct('pest_management'),
        'fertilization': collection.distinct('fertilization'),
        'irrigation': collection.distinct('irrigation'),
        'environmental_threats': collection.distinct('environmental_threats'),
        # 'total_project_cost_brl': collection.distinct('total_project_cost_brl'),
        'stage_indicator': collection.distinct('stage_indicator'),
        # 'living_trees_to_date': collection.distinct('living_trees_to_date'),
        # 'soil_fertility_index_percent': collection.distinct('soil_fertility_index_percent'),
        'water_quality_indicators': collection.distinct('water_quality_indicators')
    }
