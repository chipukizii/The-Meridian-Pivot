# solo_recon_graphql/server.py
# Standalone Flask server serving the Day 1 GraphQL Prototype Endpoint

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add root directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from solo_recon_graphql.graphql_schema import schema

app = Flask(__name__)
CORS(app)

@app.route('/graphql', methods=['GET', 'POST'])
def graphql_handler():
    if request.method == 'GET':
        # Provide HTML interactive interface / schema summary
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Northstar GraphQL Mini-Prototype Interface</title>
            <style>
                body { font-family: monospace; padding: 2rem; background: #0f172a; color: #f8fafc; }
                h1 { color: #38bdf8; }
                pre { background: #1e293b; padding: 1rem; border-radius: 8px; border: 1px solid #334155; }
                code { color: #a5f3fc; }
            </style>
        </head>
        <body>
            <h1>Northstar Inventory GraphQL Mini-Prototype (Day 1 Recon)</h1>
            <p>Send POST requests to <code>/graphql</code> with JSON body: <code>{"query": "..."}</code></p>
            <h3>Sample Query:</h3>
            <pre>
query {
  inventory(query: "shoe") {
    sku
    name
    stockCount
    inStock
    sizesAvailable
  }
}
            </pre>
            <h3>Sample Mutation:</h3>
            <pre>
mutation {
  updateStock(sku: "SKU-HOOD-03", newCount: 25) {
    success
    message
    item {
      sku
      stockCount
      inStock
    }
  }
}
            </pre>
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
    print("GraphQL Solo Prototype Server running at http://127.0.0.1:5005/graphql")
    app.run(port=5005, debug=True)
