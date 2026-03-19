from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

SWAGGER_URL = "/docs"
API_URL = "/static/open-api.yaml"

swagger_ui_blueprint = get_swaggerui_blueprint(
	SWAGGER_URL, 
 	API_URL,
	config={
		"app_name": "Book Management API"
	}
)

app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == "__main__":
  	app.run(debug=True)