# Steps để thấy docs:
- **Bước 1**: run command `python app.py`
- **Bước 2**: vào `locahost:5000/api-docs`


# Cách gen code từ openapi docs:
- **Bước 1**: run command `npx @openapitools/openapi-generator-cli generate -i openapi.yaml -g python-flask -o server-code`
- **Bước 2**: create venv enviroment: `python3.10 -m venv venv`
- **Bước 3**: `source venv/bin/activate`
- **Bước 3**: `cd server-code/` and `pip install -r requirements.txt`
- **Bước 4**: `python -m openapi_server` to run server.


