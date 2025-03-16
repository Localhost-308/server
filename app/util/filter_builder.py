
class FilterBuilder:
    def build_filters_from_request(self, params:dict):
        field_type_mapping = self.__get_field_type()
        for key, value in params.items():
            new_value = None
            if field_type_mapping[key] == int:
                new_value = int(value)
            elif field_type_mapping[key] == float:
                new_value = float(value)
            else:
                new_value = str(value)
            params[key] = new_value
        return params

    def __get_field_type(self):
        return {
            "area_id": int,
            "soil_fertility_index_percent": float,
            "avoided_co2_emissions_m3": float,
            "number_of_trees_lost": int,
            "tree_health_status": str,
            "average_tree_growth_cm": float,
            "total_precipitation_mm": float,
            "average_annual_temperature_C": float,
            "relative_humidity_percent": float,
            "wind_speed_kmh": float,
            "available_water_m3": float,
            "water_sources": str,
            "water_quality_indicators": str,
            "pest_management": str,
            "fertilization": str,
            "irrigation": str,
            "environmental_threats": str,
            "total_project_cost_brl": float,
            "financing_source": str,
            "stage_indicator": str,
            "start_month": int,
            "measurement_date": str,
            "final_total_area_hectares": float,
            "total_area_of_space_hectares": float,
            "trees_alive_so_far": int,
            "tree_survival_rate": float
        }
