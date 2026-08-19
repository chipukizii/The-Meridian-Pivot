# Day 3: Original Build Log & Architectural Report

**Sprint Phase**: Day 3 — Original Spec Build  
**Scenario**: Northstar Retail Co. Live Inventory Sync Service  
**Core Specification**: Poll warehouse API every 5 minutes, cache stock status locally, and expose unified query endpoints for support deflection.  
**Architecture Model**: Scheduled Polling Ingestion Engine + Local Data Cache + Dual Query Layer (REST & GraphQL)  

---

## 1. Overview of Day 3 Implementation

On Day 3, we transitioned from solo tool recon to building the complete **Original Specification** for Northstar Retail Co.

### Built Components:
1. **Central Warehouse Mock Feed (`warehouse_api.py`)**:
   - Simulates Northstar's upstream distribution center stock feed.
   - Endpoint: `GET /api/warehouse/stock` returning live stock counts and SKU statuses.
2. **Polling Engine (`polling_service.py`)**:
   - Background thread daemon configured for 300-second (5-minute) execution intervals.
   - Automatically invokes `sync_once()` to fetch upstream stock and update local persistence.
3. **Data Cache & Metadata Tracking (`db.py`)**:
   - Implemented `update_inventory_cache(updates)` to persist stock counts directly into JSON storage.
   - Implemented `get_sync_status()` and `update_sync_status()` tracking `lastSyncedAt`, `syncMethod: "POLLING_5MIN"`, and `totalSynced` items.
4. **Unified Flask Server & Query Layer (`app.py` & `routes.py`)**:
   - Updated `/api/inventory` to return cached items along with `syncMetadata`.
   - Mounted `/graphql` endpoint allowing GraphQL queries (`inventory`, `checkStock`) to resolve live stock from the updated cache.

---

## 2. Technical Journal & Development Log

### Activity #1: Upstream Feed & Cache Persistence Setup
- **Goal**: Establish contract between upstream warehouse data structure and local `db.py` cache.
- **Challenge**: Upstream warehouse feed uses `stockCount` and `inStock` boolean flags, while existing `inventory.json` had static entries.
- **Resolution**: Implemented `update_inventory_cache()` in `db.py` using a SKU lookup map to update item counts atomically without corrupting secondary metadata like `sizesAvailable`.

### Activity #2: Background Polling Daemon Integration
- **Goal**: Run polling loop independently from main HTTP request threads without blocking Flask web server responses.
- **Challenge**: Single-threaded Flask execution would block API responses if the 5-minute timer ran on the main thread.
- **Resolution**: Designed `PollingService` in `polling_service.py` using Python's `threading.Thread(daemon=True)`. Included a synchronous `sync_once()` method for unit testing and manual trigger execution.

### Activity #3: GraphQL & REST Dual Layer Compatibility
- **Goal**: Ensure both legacy support REST endpoints and new GraphQL schema fetch from the exact same cached data source.
- **Resolution**: Wired `graphene` resolvers in `solo_recon_graphql/graphql_schema.py` directly to `db.get_item_by_sku()` and `db.search_inventory()`. Any update committed by `polling_service.py` is instantly visible to both REST and GraphQL queries.

---

## 3. Automated Verification & Test Results

Executed automated integration test suite `test_day3_original_build.py`:

```text
....
----------------------------------------------------------------------
Ran 4 tests in 0.044s

OK
```

### Verified Test Cases:
1. `test_01_warehouse_api_endpoint`: Confirmed `GET /api/warehouse/stock` returns HTTP 200 and valid stock payload.
2. `test_02_polling_service_sync_cycle`: Confirmed `sync_once()` fetches warehouse data, updates local cache, and sets `syncMethod = 'POLLING_5MIN'`.
3. `test_03_rest_inventory_endpoint_with_sync_metadata`: Confirmed `GET /api/inventory` returns results and valid `syncMetadata`.
4. `test_04_graphql_query_serves_cached_inventory`: Confirmed GraphQL POST queries to `/graphql` resolve updated stock counts from the cache.

---

## 4. Definition of Done Checklist (Day 3)

- [x] Warehouse API polled every 5 minutes (simulated via background daemon and sync method).
- [x] Local inventory cache updated with latest stock counts.
- [x] REST query endpoint `/api/inventory` serves cached stock with sync metadata.
- [x] GraphQL query endpoint `/graphql` serves cached stock lookups.
- [x] 100% of integration tests passing (`test_day3_original_build.py`).
