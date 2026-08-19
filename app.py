# app.py — Pure API Server (Member 1 / Solo Engineer)
# Responsible for server startup, CORS configuration, blueprint routing, and GraphQL mounting.

from flask import Flask, request, jsonify
from flask_cors import CORS
from routes import api
from warehouse_api import warehouse_bp
from solo_recon_graphql.graphql_schema import schema

app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) on /api/* and /graphql routes.
CORS(app, resources={r"/*": {"origins": "*"}})

# Register blueprints
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(warehouse_bp, url_prefix='/api')

# Register GraphQL route
@app.route('/graphql', methods=['GET', 'POST'])
def graphql_handler():
    if request.method == 'GET':
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Northstar GraphQL Inventory Interface</title>
            <style>
                body { font-family: monospace; padding: 2rem; background: #0f172a; color: #f8fafc; }
                h1 { color: #38bdf8; }
                pre { background: #1e293b; padding: 1rem; border-radius: 8px; border: 1px solid #334155; }
                code { color: #a5f3fc; }
            </style>
        </head>
        <body>
            <h1>Northstar Inventory GraphQL Endpoint</h1>
            <p>Send POST requests to <code>/graphql</code> with JSON body: <code>{"query": "..."}</code></p>
        </body>
        </html>
        """

    data = request.get_json() or {}
    query = data.get('query')
    variables = data.get('variables')

    if not query:
        return jsonify({'errors': [{'message': 'Must provide query string.'}]}), 400

    result = schema.execute(query, variable_values=variables)
    response = {}
    if result.data:
        response['data'] = result.data
    if result.errors:
        response['errors'] = [{'message': str(err)} for err in result.errors]

    return jsonify(response)


if __name__ == '__main__':
    print("Northstar API & GraphQL Server running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
