from flask import Flask, send_from_directory, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return 'Welcome to the API Home Page. Go to /api-docs for documentation.'

@app.route('/api-docs')
def serve_raml_docs():
    # Serve file HTML tĩnh trong folder "static/docs"
    return send_from_directory('static', 'api-docs.html')

if __name__ == '__main__':
    app.run(debug=True)