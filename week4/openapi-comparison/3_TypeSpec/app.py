from flask import Flask, send_file
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# đường dẫn tới file OpenAPI
SWAGGER_URL = "/api-docs"
API_URL = "/openapi.json"

# Swagger UI config
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name": "Book Management API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route("/openapi.json")
def openapi():
    return send_file("tsp-output/@typespec/openapi3/openapi.json")

if __name__ == "__main__":
    app.run(debug=True)