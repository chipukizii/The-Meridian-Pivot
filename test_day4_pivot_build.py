# test_day4_pivot_build.py
# Automated Test Suite for Day 4 Pivot (Solstice Events Co. Kiosk & Webhook Model)

import unittest
import json
import hmac
import hashlib
from app import app
import db
from message_queue import printer_queue, WEBHOOK_SECRET

class TestDay4PivotBuild(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        db.reset_attendees()

    def test_01_deprecated_sync_printer_endpoint(self):
        """Verify synchronous printer endpoint returns HTTP 410 Gone (KILLED)."""
        response = self.client.post('/api/printer/print-job-sync', json={"ticketId": "ATT-1001"})
        self.assertEqual(response.status_code, 410)
        data = response.get_json()
        self.assertEqual(data['error'], 'DEPRECATED_ENDPOINT')
        self.assertEqual(data['status'], 'KILLED')

    def test_02_async_kiosk_scan_checkin_pending_state(self):
        """Verify staff QR scan enqueues print job and returns status PENDING_PRINT."""
        payload = {"ticketId": "ATT-1001"}
        response = self.client.post('/api/kiosk/checkin', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'PENDING_PRINT')
        self.assertIn('jobId', data)
        self.assertEqual(data['attendee']['status'], 'PENDING_PRINT')

    def test_03_duplicate_scan_protection(self):
        """Verify duplicate QR scan for an attendee in PENDING_PRINT or CHECKED_IN is rejected."""
        # First scan -> Pending
        self.client.post('/api/kiosk/checkin', json={"ticketId": "ATT-1001"})

        # Duplicate scan -> Must be rejected
        response = self.client.post('/api/kiosk/checkin', json={"ticketId": "ATT-1001"})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'DUPLICATE_SCAN_REJECTED')

    def test_04_webhook_callback_hmac_and_confirmation(self):
        """Verify Webhook Callback validates HMAC signature and updates attendee to CHECKED_IN."""
        # Initiate checkin
        scan_res = self.client.post('/api/kiosk/checkin', json={"ticketId": "ATT-1002"}).get_json()
        job_id = scan_res['jobId']

        # 1. Test invalid HMAC signature -> 401
        webhook_payload = {
            "event": "BADGE_PRINT_COMPLETED",
            "jobId": job_id,
            "ticketId": "ATT-1002",
            "status": "SUCCESS",
            "badgeId": "BDG-998877"
        }
        raw_body = json.dumps(webhook_payload).encode('utf-8')
        invalid_resp = self.client.post(
            '/api/webhooks/badge-printed',
            data=raw_body,
            headers={'Content-Type': 'application/json', 'X-Printer-Signature': 'invalid_sig'}
        )
        self.assertEqual(invalid_resp.status_code, 401)

        # 2. Test valid HMAC signature -> 200 CHECKED_IN
        valid_sig = hmac.new(WEBHOOK_SECRET.encode('utf-8'), raw_body, hashlib.sha256).hexdigest()
        valid_resp = self.client.post(
            '/api/webhooks/badge-printed',
            data=raw_body,
            headers={'Content-Type': 'application/json', 'X-Printer-Signature': valid_sig}
        )
        self.assertEqual(valid_resp.status_code, 200)
        valid_data = valid_resp.get_json()
        self.assertTrue(valid_data['success'])
        self.assertEqual(valid_data['status'], 'CHECKED_IN')
        self.assertEqual(valid_data['attendee']['badgeId'], 'BDG-998877')

    def test_05_graphql_scan_and_status_query(self):
        """Verify GraphQL mutation initiates checkin and query fetches attendee status."""
        mutation_payload = {
            "query": """
            mutation {
                scanAttendeeQr(ticketId: "ATT-1003") {
                    success
                    message
                    status
                    attendee {
                        ticketId
                        name
                        status
                    }
                }
            }
            """
        }
        res = self.client.post('/graphql', json=mutation_payload)
        self.assertEqual(res.status_code, 200)
        res_data = res.get_json()
        self.assertTrue(res_data['data']['scanAttendeeQr']['success'])
        self.assertEqual(res_data['data']['scanAttendeeQr']['status'], 'PENDING_PRINT')

        # Query GraphQL status
        query_payload = {
            "query": """
            query {
                attendeeStatus(ticketId: "ATT-1003") {
                    ticketId
                    name
                    status
                }
            }
            """
        }
        q_res = self.client.post('/graphql', json=query_payload)
        self.assertEqual(q_res.status_code, 200)
        q_data = q_res.get_json()
        self.assertEqual(q_data['data']['attendeeStatus']['status'], 'PENDING_PRINT')

    def test_06_three_attendees_full_lifecycle(self):
        """Verify full lifecycle across all 3 test attendees (ATT-1001, ATT-1002, ATT-1003)."""
        for t_id in ["ATT-1001", "ATT-1002", "ATT-1003"]:
            # Scan
            s_res = self.client.post('/api/kiosk/checkin', json={"ticketId": t_id}).get_json()
            job_id = s_res['jobId']

            # Confirm Webhook
            w_body = json.dumps({"event": "BADGE_PRINT_COMPLETED", "jobId": job_id, "ticketId": t_id, "badgeId": f"BDG-{t_id}"}).encode('utf-8')
            sig = hmac.new(WEBHOOK_SECRET.encode('utf-8'), w_body, hashlib.sha256).hexdigest()
            self.client.post('/api/webhooks/badge-printed', data=w_body, headers={'Content-Type': 'application/json', 'X-Printer-Signature': sig})

            # Check status
            st = self.client.get(f'/api/kiosk/status/{t_id}').get_json()
            self.assertEqual(st['attendee']['status'], 'CHECKED_IN')
            self.assertTrue(st['attendee']['badgePrinted'])

if __name__ == '__main__':
    unittest.main()
