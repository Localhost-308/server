chat_template = f"""
---
**Contextualização:**

O objetivo deste processo é gerar um **único relatório consolidado** sobre o reflorestamento de uma área específica para o proprietário. 
Enviarei uma lista contendo informações dessa área referentes a diferentes datas. Com esses dados consolidados, 
você deverá gerar um relatório formal e padronizado que ofereça uma visão geral da situação do reflorestamento ao longo do tempo.

---
**Definição de Padrões:**

Para garantir a consistência dos relatórios, siga as seguintes instruções:

**Template:** O template abaixo define a estrutura de cada relatório. Não crie tópicos fora desta estrutura para manter o padrão.

**Dados:** Enviarei os dados como uma lista de objetos (ou dicionários), onde cada objeto conterá as informações da mesma área e empresa, mas referentes a datas diferentes.

**Formato de Resposta:** Todas as suas respostas devem ser formatadas em Markdown.

**Envio:** Enviarei o template apenas uma vez. Nas mensagens subsequentes, enviarei somente os dados, e você deverá gerar o relatório com base no template fornecido.

---
**Observações sobre o Template:**

* **Edição de Campos:** Os campos entre `<>` devem ser editados com as informações correspondentes da lista de dados fornecida. Observe que os placeholders seguem o formato `<campo: nome_do_campo>`, indicando qual campo dos seus dados deve ser utilizado. A estrutura do relatório abaixo define como esses campos estão organizados por tópicos, agrupando informações relacionadas.
* **Formatação:** O template fornecido não possui listas ou negritos. Você tem a liberdade de adicionar essa formatação da maneira que achar mais adequada para melhorar a apresentação, mantendo a mesma formatação para todos os relatórios.
* **Tabelas:** Não inclua tabelas nos relatórios.
* **Formato de Saída:** Retorne sempre a resposta em formato Markdown.

---
**Template:**

## Relatório de Reflorestamento - <nome da area>

### Descrição da Área:
Com base nos dados fornecidos, gere uma breve descrição da área de reflorestamento, incluindo informações como estágio geral e principais características observadas.

### Informações da Área:
* Período: <data da primeira medição e da ultima, exemplo: Janeiro a Abril de 2025>
* Área: <nome da area>
* Área Total: <campo: total_area_hectares>
* Área Inicial Plantada: <campo: initial_planted_area_hectares>
* Estágio Atual: <estagio da ultima medição - campo: stage_indicator>
* Técnicas de Plantio: <campo: planting_techniques>
* Ameaças Ambientais: <ameaça da ultima medição - campo: environmental_threats>

### Indicadores Ecológicos
* Crescimento Médio das Árvores: <media do crescimento das arvores de toda as medições - campo: average_tree_growth_cm>
* Emissões de CO2 Evitadas (Total): <total de CO2 evitado - campo: avoided_co2_emissions_cubic_meters>
* Qualidade da Água: <campo: water_quality_indicators>
* Fontes de Água: <campo: water_sources>
* Fertilidade do Solo: <campo: soil_fertility_index_percent>

### Saúde e Manutenção
* Árvores Vivas (Total): <campo: living_trees_to_date>
* Árvores Perdidas (Total): <campo: number_of_trees_lost>
* Espécies Plantadas: <campo: planted_species>
* Cobertura Vegetal Inicial: <campo: initial_vegetation_cover>
* Saúde das Árvores: <campo: tree_health_status>
* Manejo de Pragas: <campo: pest_management>
* Tipo de Irrigação: <campo: irrigation>
* Tipo de Fertilização: <campo: fertilization>

### Recomendações:
Com base na análise dos dados, apresente no máximo 5 recomendações em formato de tópicos para o manejo e a melhoria do reflorestamento.
"""

graph_analysis = """
### Analise dos dados

Este gráfico apresenta a evolução mensal de três indicadores importantes: o número de árvores vivas, a quantidade de árvores perdidas e o volume de CO2 evitado. Ao observar as linhas, podemos identificar as tendências ao longo do tempo, como o crescimento ou declínio do número de árvores e o impacto nas emissões de CO2 evitadas em cada mês.

![Análise de Tendência por Mês](<<path_image_1>>)

Este gráfico de área ilustra a evolução da quantidade de árvores vivas e perdidas ao longo do tempo. As áreas coloridas mostram como esses dois grupos se comportaram mês a mês, permitindo visualizar de forma clara o balanço entre o ganho e a perda de árvores no período analisado.

![Evolução das Árvores Vivas e Perdidas](<<path_image_2>>)
"""
