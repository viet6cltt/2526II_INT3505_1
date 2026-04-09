# Steps:
- **Bước 1**: run command `npm install`
- **Bước 2**: run command `npx tsp compile .`
- **Bước 3**: run command `python app.py`
- **Bước 4**: vào `locahost:5000/api-docs`


# Sinh code:
- **Bước 1**: `npx @openapitools/openapi-generator-cli generate -i ./tsp-output/@typespec/openapi3/openapi.json -g python-flask -o server-code`
- **Bước 2**: create venv enviroment: `python3.10 -m venv venv`
- **Bước 3**: `source venv/bin/activate`
- **Bước 4**: `cd server-code/` and `pip install -r requirements.txt`
- **Bước 5**: `python -m openapi_server` to run server.