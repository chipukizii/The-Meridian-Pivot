# app.py — Pure API Server (Member 1)
# Responsible only for server startup, CORS configuration, and blueprint routing.

from flask import Flask
from flask_cors import CORS
from routes import api

app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) on /api/* routes.
# This allows the Frontend Developer to fetch data while running their UI server.
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register all endpoints defined in routes.py under the /api prefix.
app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    print("Northstar API Server running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
