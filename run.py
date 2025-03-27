from app.controllers import area, company, localization, user, area_information, import_file, reforestation_stage, environment_threats
from app.initializer import app

app.register_blueprint(user.users)
app.register_blueprint(area.areas)
app.register_blueprint(company.companies)
app.register_blueprint(localization.localizations)
app.register_blueprint(area_information.area_information)
app.register_blueprint(import_file.files)
app.register_blueprint(reforestation_stage.reforestation)
app.register_blueprint(environment_threats.environment_threats)