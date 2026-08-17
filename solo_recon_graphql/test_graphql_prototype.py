# solo_recon_graphql/test_graphql_prototype.py
# Automated Verification Test Suite for Day 1 GraphQL Solo Recon Prototype

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from solo_recon_graphql.graphql_schema import schema
from solo_recon_graphql.server import app

class TestGraphQLPrototype(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_direct_schema_inventory_query(self):
        """Test searching inventory via GraphQL schema execution directly."""
        query = """
        query {
            inventory(query: "Headphones") {
                sku
                name
                category
                stockCount
                inStock
            }
        }
        """
        result = schema.execute(query)
        self.assertIsNone(result.errors)
        data = result.data['inventory']
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]['sku'], "SKU-AUDIO-02")
        self.assertTrue(data[0]['inStock'])

    def test_direct_schema_stock_check(self):
        """Test stock checking query with requested quantity."""
        query = """
        query {
            checkStock(sku: "SKU-SHOE-01", requestedQuantity: 10) {
                sku
                available
                stockCount
                message
            }
        }
        """
        result = schema.execute(query)
        self.assertIsNone(result.errors)
        stock_data = result.data['checkStock']
        self.assertEqual(stock_data['sku'], "SKU-SHOE-01")
        self.assertTrue(stock_data['available'])
        self.assertEqual(stock_data['stockCount'], 42)

    def test_direct_schema_stock_mutation(self):
        """Test updating stock count via GraphQL Mutation."""
        mutation = """
        mutation {
            updateStock(sku: "SKU-HOOD-03", newCount: 50) {
                success
                message
                item {
                    sku
                    stockCount
                    inStock
                }
            }
        }
        """
        result = schema.execute(mutation)
        self.assertIsNone(result.errors)
        res = result.data['updateStock']
        self.assertTrue(res['success'])
        self.assertEqual(res['item']['stockCount'], 50)
        self.assertTrue(res['item']['inStock'])

    def test_http_endpoint_post(self):
        """Test sending GraphQL POST query to HTTP server endpoint."""
        payload = {
            "query": """
            query {
                itemBySku(sku: "SKU-BOTT-04") {
                    name
                    category
                    price
                }
            }
            """
        }
        response = self.client.post('/graphql', json=payload)
        self.assertEqual(response.status_code, 200)
        json_resp = response.get_json()
        self.assertIn('data', json_resp)
        self.assertEqual(json_resp['data']['itemBySku']['name'], "Insulated Thermal Water Bottle (1L)")

if __name__ == '__main__':
    unittest.main()
