# Assignment 1: Independent Learning & Blocker Journal
**Learner Name**: [Your Name / Member ID]  
**Assigned Unfamiliar Tool**: GraphQL Integration (Python Graphene Framework)  
**Target Scenario**: Northstar Retail Co. Inventory Sync Service  
**Timebox Goal**: 4 Hours | **Actual Time Spent**: 3 Hours 30 Minutes  

---

## 1. Executive Summary & Prototype Overview
For the Day 1–2 Solo Recon phase, I was privately assigned **GraphQL**, a query language and schema framework completely unfamiliar to me. I built a self-contained mini-prototype using Python's `graphene` library integrated with Flask.

The mini-prototype exposes a GraphQL endpoint (`/graphql`) that permits:
1. Flexible inventory searching across names, SKUs, and categories without over-fetching payload fields.
2. Real-time availability checking (`checkStock`) against requested item quantities.
3. Asynchronous stock mutations (`updateStock`) to dynamically alter inventory stock counts.

All code was developed independently without technical advice from teammates or instructors, as required by sprint autonomy rules.

---

## 2. Time-Boxing & Resource Efficiency Log

| Phase | Planned Time | Actual Time | Output |
| :--- | :--- | :--- | :--- |
| **Phase 1: Conceptual Recon & Spec Reading** | 0h 45m | 0h 40m | Read GraphQL specification, schema types, query/mutation paradigms. |
| **Phase 2: Schema Design & Type Definition** | 1h 00m | 0h 50m | Drafted `InventoryItemType`, `Query`, and `UpdateStockMutation`. |
| **Phase 3: Resolver Implementation & Data Binding**| 1h 15m | 1h 10m | Bound resolvers to local data layer (`db.py`). |
| **Phase 4: Flask HTTP Endpoint & Interface** | 0h 30m | 0h 25m | Implemented `/graphql` POST route and browser view. |
| **Phase 5: Automated Testing & Verification** | 0h 30m | 0h 25m | Wrote 4 automated unit tests verifying schema & HTTP. |
| **Total** | **4h 00m** | **3h 30m** | **Completed within budget (12.5% time buffer saved).** |

---

## 3. Real-Time Blocker & Troubleshooting Log

### Blocker #1: Graphene CamelCase Attribute Conversion Mismatch
- **Timestamp**: Day 1, 11:15 AM
- **Error / Log Output**:
  ```text
  graphql.error.graphql_error.GraphQLError: Cannot return null for non-nullable field InventoryItemType.inStock.
  ```
- **Symptom**: Querying `inStock` returned `null` even though `inventory.json` contained `"inStock": true`.
- **Hypothesis**: `graphene` automatically converts snake_case field names (`in_stock`) to camelCase (`inStock`) in GraphQL schemas, but failed to automatically map Python dict keys formatted in camelCase.
- **Resources Consulted**:
  - Graphene Python Documentation on ObjectTypes & Resolvers (https://docs.graphene-python.org/en/latest/types/objecttypes/)
  - StackOverflow: *"Graphene python dictionary field mapping null"*
- **Autonomous Fix**: Added explicit resolver methods (`resolve_in_stock`, `resolve_stock_count`) using dict `.get('inStock')` to handle the key mapping reliably:
  ```python
  def resolve_in_stock(root, info):
      return root.get('inStock', False)
  ```

---

### Blocker #2: Resolver Function Arguments (`root` & `info` Signature error)
- **Timestamp**: Day 1, 12:40 PM
- **Error / Log Output**:
  ```text
  TypeError: Query.resolve_inventory() takes 2 positional arguments but 3 were given
  ```
- **Symptom**: Schema execution crashed whenever a query passed field arguments like `inventory(query: "shoe")`.
- **Hypothesis**: I assumed resolver methods only received `(self, query)`. However, Graphene passes `root` (parent object) and `info` (context metadata) before field parameters.
- **Resources Consulted**:
  - Graphene Execution Docs: Resolver Signatures
  - Python `inspect` module traceback
- **Autonomous Fix**: Updated all field resolver signatures to explicitly accept `(root, info, **args)`:
  ```python
  def resolve_inventory(root, info, query=""):
      return db.search_inventory(query)
  ```

---

### Blocker #3: Mutation Argument Extraction & Class Structure
- **Timestamp**: Day 1, 01:45 PM
- **Error / Log Output**:
  ```text
  AttributeError: 'UpdateStockMutation' object has no attribute 'mutate'
  ```
- **Symptom**: Executing `mutation { updateStock(...) }` returned an AttributeError on schema compilation.
- **Hypothesis**: I placed the `mutate()` method outside of the `UpdateStockMutation` class definition due to an indentation typo.
- **Resources Consulted**:
  - Graphene Mutations Guide (https://docs.graphene-python.org/en/latest/types/mutations/)
- **Autonomous Fix**: Nesting `mutate()` as a `@classmethod` or standard method inside `class UpdateStockMutation(graphene.Mutation):` and defining `class Arguments:` inside the mutation scope.

---

### Blocker #4: Flask POST JSON Request Parsing for GraphQL Execution
- **Timestamp**: Day 1, 02:20 PM
- **Error / Log Output**:
  ```text
  TypeError: execute() missing 1 required positional argument: 'request_string'
  ```
- **Symptom**: HTTP POST requests sent via `curl` failed with a 500 internal error.
- **Hypothesis**: The Flask route was passing the full JSON dictionary directly into `schema.execute()` instead of extracting the string value under the `"query"` key.
- **Resources Consulted**:
  - GraphQL HTTP Spec: `POST /graphql` body format (`{"query": "...", "variables": {...}}`)
- **Autonomous Fix**: Extracted `data.get('query')` and `data.get('variables')` before executing:
  ```python
  data = request.get_json() or {}
  result = schema.execute(data.get('query'), variable_values=data.get('variables'))
  ```

---

## 4. Key Learnings & Tool Mastery Assessment

1. **Schema-First Contract**: GraphQL enforces strict typing on fields. Unlike REST where endpoints return arbitrary JSON structures, GraphQL queries select only required fields, conserving network bandwidth.
2. **Single Endpoint Architecture**: Eliminates over-fetching and under-fetching by funneling queries and mutations through a single `/graphql` HTTP route.
3. **Preparedness for Sprint Pivot**: Because this GraphQL layer wraps the underlying `db.py` functions, it can easily digest new data structures or real-time event payloads introduced later in the sprint.

---

## 5. Verification & Test Evidence
Automated test suite `solo_recon_graphql/test_graphql_prototype.py` executed successfully:
```text
Ran 4 tests in 0.050s

OK (Direct Query Test, Stock Availability Test, Mutation Test, HTTP POST Test)
```
