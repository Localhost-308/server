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
        df_area = df[['measurement_date', 'number_of_trees_lost', 'living_trees_to_date']]
        df_area['date_label'] = df_area['measurement_date'].dt.strftime('%Y-%m')
        cores = ['#2ca02c', '#d62728']
        plt.figure(figsize=(12, 6))
        plt.stackplot(df_area['date_label'], df_area['living_trees_to_date'], df_area['number_of_trees_lost'], labels=["Árvores Vivas", "Árvores Perdidas"], alpha=0.6, colors=cores)
        plt.title("Evolução das Árvores Vivas e Perdidas")
        plt.xlabel("Data")
        plt.ylabel("Quantidade de Árvores")
        plt.xticks(rotation=45)
        plt.legend(loc="upper left")
        plt.tight_layout()
        plt.savefig(path, dpi=dpi)
