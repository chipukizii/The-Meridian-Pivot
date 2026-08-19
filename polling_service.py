# polling_service.py — Day 3 Polling Engine
# Responsible for: Polling the Warehouse API every 5 minutes and updating local stock cache in db.py.
# WARNING: This module represents the Day 3 Polling Spec (scheduled for retirement on Day 4 Pivot).

import time
import threading
import datetime
import urllib.request
import json
import db

POLL_INTERVAL_SECONDS = 300  # 5 minutes per spec (configurable for testing)
DEFAULT_WAREHOUSE_URL = "http://127.0.0.1:5000/api/warehouse/stock"

class PollingService:
    def __init__(self, target_url=DEFAULT_WAREHOUSE_URL, interval=POLL_INTERVAL_SECONDS):
        self.target_url = target_url
        self.interval = interval
        self.running = False
        self._thread = None
        self.last_poll_time = None
        self.poll_count = 0

    def sync_once(self):
        """Execute a single polling cycle against the Warehouse API."""
        try:
            req = urllib.request.Request(self.target_url, headers={'User-Agent': 'Northstar-PollingEngine/1.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    payload = json.loads(response.read().decode('utf-8'))
                    inventory_data = payload.get('inventory', [])
                    updated = db.update_inventory_cache(inventory_data)
                    self.last_poll_time = datetime.datetime.now().isoformat()
                    self.poll_count += 1
                    print(f"[{self.last_poll_time}] [PollingEngine] Successfully synced {updated} items from warehouse.")
                    return True, updated
        except Exception as e:
            print(f"[PollingEngine Error] Polling cycle failed: {e}")
            return False, 0

    def _loop(self):
        print(f"[PollingEngine] Daemon started. Polling {self.target_url} every {self.interval} seconds.")
        while self.running:
            self.sync_once()
            time.sleep(self.interval)

    def start(self):
        """Start background polling daemon thread."""
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def stop(self):
        """Stop background polling daemon thread."""
        self.running = False
        print("[PollingEngine] Polling daemon stopped.")

# Global singleton polling engine instance
polling_engine = PollingService()
