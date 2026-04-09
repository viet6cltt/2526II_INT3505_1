# Steps:
- **Bước 1**: run command `npm install -g aglio`
- **Bước 2**: run command `aglio -i ./static/api-docs.apiblueprint -o ./static/api-docs.html`
- **Bước 3**: run command `python app.py`
- **Bước 4**: vào `locahost:5000/api-docs`

# Cách sinh code:
- **Bước 1**: `npx apib2swagger -i ./static/api-docs.apiblueprint -o ./static/openapi.yaml --yaml --target-version 3`
- **Buớc 2**: `npx @openapitools/openapi-generator-cli generate -i ./static/openapi.yaml -g python-flask -o server-code`
- **Bước 3**: create venv enviroment: `python3.10 -m venv venv`
- **Bước 4**: `source venv/bin/activate`
- **Bước 5**: `cd server-code/` and `pip install -r requirements.txt`
- **Bước 6**: `python -m openapi_server` to run server.