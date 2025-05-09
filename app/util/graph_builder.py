import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class GraphBuilder:
    def plot_trend_analysis(self, data, path, dpi=300):
        df = pd.DataFrame(data)
        df['measurement_date'] = pd.to_datetime(df['measurement_date'])
        df['year_month'] = df['measurement_date'].dt.to_period('M')
        df_monthly = df.groupby('year_month').agg({
            'living_trees_to_date': 'sum',
            'number_of_trees_lost': 'sum',
            'avoided_co2_emissions_cubic_meters': 'sum'
        }).reset_index()

        plt.figure(figsize=(12, 6))
        plt.plot(df_monthly['year_month'].astype(str), df_monthly['living_trees_to_date'], label='Árvores Vivas', marker='o', color='green')
        plt.plot(df_monthly['year_month'].astype(str), df_monthly['number_of_trees_lost'], label='Árvores Perdidas', marker='o', color='red')
        plt.plot(df_monthly['year_month'].astype(str), df_monthly['avoided_co2_emissions_cubic_meters'], label='CO2 Evitado', marker='o', color='blue')
        plt.title('Análise de Tendência por Mês')
        plt.xlabel('Data')
        plt.ylabel('Valores (quantidade de árvores e CO2 evitado)')
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(path, dpi=dpi)

    def plot_area_evolution(self, data, path, dpi=300):
        df = pd.DataFrame(data)
        df['measurement_date'] = pd.to_datetime(df['measurement_date'])
        df_sorted = df.sort_values(by='measurement_date')

        first = df_sorted.iloc[0]
        last = df_sorted.iloc[-1]

        water_quality_score = {'Muito boa': 100, 'Boa': 75, 'Razoável': 50}

        labels = [
            "Fertilidade do Solo (%)",
            "Crescimento Médio (cm)",
            "CO2 Evitado (x100 m³)",
            "Taxa de Sobrevivência (%)",
            "Qualidade da Água (%)"
        ]

        first_values = [
            first['soil_fertility_index_percent'],
            first['average_tree_growth_cm'],
            first['avoided_co2_emissions_cubic_meters'] * 100,
            first['tree_survival_rate'],
            water_quality_score.get(first['water_quality_indicators'], 0)
        ]

        last_values = [
            last['soil_fertility_index_percent'],
            last['average_tree_growth_cm'],
            last['avoided_co2_emissions_cubic_meters'] * 100,
            last['tree_survival_rate'],
            water_quality_score.get(last['water_quality_indicators'], 0)
        ]

        first_values += first_values[:1]
        last_values += last_values[:1]

        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(12, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, first_values, label=first['measurement_date'].strftime('%b/%Y'), linewidth=2)
        ax.fill(angles, first_values, alpha=0.25)
        ax.plot(angles, last_values, label=last['measurement_date'].strftime('%b/%Y'), linewidth=2)
        ax.fill(angles, last_values, alpha=0.25)
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.degrees(angles[:-1]), labels)
        ax.set_title('Evolução dos Indicadores Ambientais')
        ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
        plt.tight_layout()
        plt.savefig(path, dpi=dpi)
