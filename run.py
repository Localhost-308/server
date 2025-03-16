from app.controllers import area, company, localization, user, area_information
from app.initializer import app

app.register_blueprint(user.users)
app.register_blueprint(area.areas)
app.register_blueprint(company.companies)
app.register_blueprint(localization.localizations)
app.register_blueprint(area_information.area_information)
