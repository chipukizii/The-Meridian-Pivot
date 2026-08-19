# test_day3_original_build.py
# Automated Verification Test Suite for Day 3 Original Polling Build

import unittest
from app import app
import db
from polling_service import PollingService

class TestDay3OriginalBuild(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_01_warehouse_api_endpoint(self):
        """Verify warehouse API returns live stock feed."""
        response = self.client.get('/api/warehouse/stock')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('inventory', data)
        self.assertGreaterEqual(len(data['inventory']), 1)

    def test_02_polling_service_sync_cycle(self):
        """Verify polling service fetches warehouse stock and updates local cache."""
        # Use test client wrapper or direct sync logic
        warehouse_resp = self.client.get('/api/warehouse/stock')
        wh_data = warehouse_resp.get_json().get('inventory', [])
        
        # Execute cache sync
        updated_count = db.update_inventory_cache(wh_data)
        self.assertGreaterEqual(updated_count, 1)

        # Check sync status metadata
        sync_meta = db.get_sync_status()
        self.assertEqual(sync_meta['syncMethod'], 'POLLING_5MIN')
        self.assertIsNotNone(sync_meta['lastSyncedAt'])

    def test_03_rest_inventory_endpoint_with_sync_metadata(self):
        """Verify REST query endpoint reflects cached inventory and sync metadata."""
        response = self.client.get('/api/inventory?q=shoes')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('syncMetadata', data)
        self.assertIn('results', data)

    def test_04_graphql_query_serves_cached_inventory(self):
        """Verify GraphQL endpoint queries cached inventory updated by polling engine."""
        payload = {
            "query": """
            query {
                inventory(query: "shoe") {
                    sku
                    name
                    stockCount
                    inStock
                }
            }
            """
        }
        response = self.client.post('/graphql', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('data', data)
        items = data['data']['inventory']
        self.assertGreaterEqual(len(items), 1)
        self.assertEqual(items[0]['sku'], 'SKU-SHOE-01')

if __name__ == '__main__':
    unittest.main()
