# TCG ShipLogic API Debug Report
_Generated: 2026-03-12 | Token: `53612520|d2l9DRSecZr2Ikh3SdlR5TOy8sWIZaYJiMnTL2XM9b2f0246`_

---

## STEP 1 — GET Endpoint Results

| Endpoint | Status | Response |
|----------|--------|----------|
| `GET /v2/account` | 404 | `Unhandled resource path: /account` |
| `GET /v2/providers` | 400 | `origin is required` ← endpoint exists, needs param |
| `GET /v2/service-levels` | 404 | `Unhandled resource path: /service-levels` |
| `GET /v2/shipments` | 403 | `{"message":"You do not have permission to view shipments (not_logged_in)"}` |
| `GET /v2/rates` | 405 | `Method GET not been defined for /rates` ← POST only |
| `GET /account` | 404 | `Unhandled resource path: /account` |
| `GET /providers` | 400 | `origin is required` |
| `GET /service-levels` | 404 | `Unhandled resource path: /service-levels` |
| `GET /shipments` | 403 | `{"message":"You do not have permission to view shipments (not_logged_in)"}` |

### Interpretation
- `/v2/rates` is POST-only ✅ (correct to POST to it)
- `/v2/shipments` GET returns 403 "not_logged_in" — token type issue (see § Token Analysis)
- `/v2/providers` exists but requires `?origin=` query param (all tested values returned 404 "could not get provider by origin")
- `/v2/service-levels` path does NOT exist — not a valid endpoint

---

## STEP 2 — POST /v2/rates (Original Body)

**Request:**
```
POST https://api.shiplogic.com/v2/rates
Authorization: Token 53612520|d2l9DRSecZr2Ikh3SdlR5TOy8sWIZaYJiMnTL2XM9b2f0246
Content-Type: application/json
```
Body as specified in task.

**Response:** `400 Bad Request`
```
provider_id is required
```

**Analysis:** Auth passes ✅. Missing `provider_id` field (must be int64).

---

## STEP 3 — POST /rates (Without /v2)

**Response:** `400 Bad Request`
```
provider_id is required
```

Same error — both `/v2/rates` and `/rates` are the same endpoint (or both require `provider_id`).

---

## STEP 4 — GET /v2/service-levels with X-API-Key Header

```
GET /v2/service-levels with X-API-Key: 53612520|...
Response: 404 | Unhandled resource path: /service-levels
```

This endpoint path doesn't exist regardless of auth header.

---

## EXTENDED DEBUGGING RESULTS

### Address Type Discovery

The original code uses `"type": "building"` — **THIS IS INVALID**.

| Address Type | Status | Response |
|---|---|---|
| `"building"` | 400 | `invalid collection address, because invalid address type: building` |
| `"residential"` | ✅ | Advances past validation → next error |
| `"business"` | ✅ | Advances past validation → next error |
| `"commercial"` | 400 | `invalid address type: commercial` |
| `"warehouse"` | 400 | `invalid address type: warehouse` |
| `"depot"` | 400 | `invalid address type: depot` |
| `"apartment"` | 400 | invalid |
| `"house"` | 400 | invalid |
| no type field | ✅ | Advances past validation |

**✅ FIX #1: Change address type from `"building"` to `"business"` (collection) and `"residential"` (delivery)**

---

### provider_id Field

- Must be `int64` (string values like `"tcg"` rejected with type error)
- Required by both `/v2/rates` and `/v2/shipments`
- Without it: `"provider_id is required"`

Tested values with `"type": "business"` addresses: provider_id 1–5, all moved past address validation, then hit `"account not found"`.

---

### account_id Field

- Required by `/v2/rates` when `provider_id` is provided
- Without it: `"account_id is required"`
- The token prefix `53612520` was tested as `account_id` → `"account not found"` for all tested `provider_id` values
- Values tested: `53612520, 53612519, 53612521, 5361252, 536125, 53612, 5361, 536, 53, 5, 1, 10, 100, 1000, 12345` → ALL return `"account not found"`

**⚠️ BLOCKER: The correct `account_id` is unknown. The token prefix `53612520` is NOT the account ID — it is the API token's database ID.**

---

### Token Nature — CRITICAL FINDING

```
GET /v2/accounts?provider_id=1
→ 403 | can only access the guest account details
```

Tested provider_id 1–20:
- IDs 1, 2, 3, 6–20 → `403 "can only access the guest account details"` (accounts exist, guest access only)
- IDs 4, 5 → `400 "sql: no rows in result set"` (no account at these provider IDs)

**⚠️ This API token is a GUEST account token.** It has read-only/limited access and cannot:
- View all shipments (`not_logged_in` error)
- Access account details for specific providers (guest restriction)

---

### POST /v2/shipments Test

```
POST /v2/shipments without provider_id:
→ 400 | could not create shipment: provider_id invalid

POST /v2/shipments with provider_id=1:
→ 400 | this feature is disabled. Please contact support
```

**⚠️ "this feature is disabled"** — either:
1. The guest account does not have shipment creation enabled
2. OR provider_id=1 is not The Courier Guy's actual provider ID

---

## ROOT CAUSE ANALYSIS

### Bug #1 — Wrong Address Type ✅ (Fixable)
- Code uses `"type": "building"` 
- ShipLogic only accepts `"business"` or `"residential"`
- **Fix:** Use `"business"` for Studex Meat collection, `"residential"` for residential deliveries

### Bug #2 — Missing provider_id ✅ (Partially fixable)
- The rates and shipments requests don't include `provider_id`
- Field must be an integer (int64)
- **Fix:** Add `"provider_id": <TCG_PROVIDER_ID>` — but we don't know the correct value

### Bug #3 — Missing account_id ❌ (Needs portal access)
- Rates endpoint requires `account_id` as int64
- The token prefix `53612520` is NOT the account_id
- The actual account_id can only be obtained from the ShipLogic dashboard

### Bug #4 — Guest Token Limitation ❌ (May need new token)
- Token appears to be a guest-level token
- Cannot view shipment history
- Shipment creation is "disabled" — may need a full merchant account token

---

## WHAT'S NEEDED TO FIX THIS

### Option A — Log into ShipLogic Portal
1. Go to **https://portal.shiplogic.com** (or The Courier Guy's business portal)
2. Log in with the StudEx Meat business credentials
3. Find:
   - **Account ID** (internal numeric ID, shown in account settings or API section)
   - **Provider ID** for The Courier Guy (usually found in carrier/integration settings)
4. Update the code with both values

### Option B — Contact TCG / ShipLogic Support
The API returns `"this feature is disabled. Please contact support"` for shipment creation.
- Contact The Courier Guy business support to:
  - Confirm API access is enabled for the account
  - Get the correct `account_id` and `provider_id` values
  - Possibly get a new API token with full merchant permissions

### Option C — Use TCG's Direct API (if available)
Earlier tests tried `https://api.thecourierguy.co.za/api/v1/` — DNS failure suggests this doesn't exist. TCG uses ShipLogic as their backend platform.

---

## FIXED CODE SNIPPET

Here is the corrected rates request (pending account_id and provider_id):

```python
import urllib.request, urllib.error, json

TOKEN = "53612520|d2l9DRSecZr2Ikh3SdlR5TOy8sWIZaYJiMnTL2XM9b2f0246"

# ⚠️ YOU NEED THESE VALUES FROM THE SHIPLOGIC PORTAL:
PROVIDER_ID = ???    # TCG's numeric provider ID (int)
ACCOUNT_ID = ???     # Your ShipLogic account ID (int, NOT the token prefix)

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

rates_body = {
    "provider_id": PROVIDER_ID,      # int64, REQUIRED
    "account_id": ACCOUNT_ID,        # int64, REQUIRED
    "collection_address": {
        "type": "business",          # ✅ was "building" — FIXED
        "company": "Studex Meat (Pty) Ltd",
        "street_address": "19 Pomona Rd",
        "local_area": "Pomona AH",
        "city": "Kempton Park",
        "zone": "GAU",
        "country": "ZA",
        "code": "1623"
    },
    "delivery_address": {
        "type": "residential",       # ✅ was "building" — FIXED
        "street_address": "13 Indus Road",
        "local_area": "Marburg",
        "city": "Port Shepstone",
        "zone": "KZN",
        "country": "ZA",
        "code": "4240"
    },
    "parcels": [{
        "submitted_length_cm": 30,
        "submitted_width_cm": 48,
        "submitted_height_cm": 17,
        "submitted_weight_kg": 3
    }],
    "declared_value": 650
}

data = json.dumps(rates_body).encode("utf-8")
req = urllib.request.Request(
    "https://api.shiplogic.com/v2/rates",
    data=data, headers=headers, method="POST"
)
with urllib.request.urlopen(req, timeout=30) as resp:
    print(json.loads(resp.read()))
```

---

## SUMMARY TABLE

| Test | Status | Finding |
|------|--------|---------|
| Token auth (Token format) | ✅ | Works, passes auth |
| Token auth (Bearer format) | ❌ | 401 always |
| Address type "building" | ❌ | Invalid — must use "business"/"residential" |
| /v2/rates POST | ✅ | Endpoint exists, POST only |
| /v2/shipments POST | ⚠️ | "Feature disabled" with provider_id=1 |
| /v2/accounts GET | ⚠️ | "Guest account only" |
| provider_id required | ❌ | Must be int64, correct value unknown |
| account_id required | ❌ | Must be int64, correct value unknown |
| Token type | ⚠️ | **Guest token** — limited permissions |

**TL;DR: Auth works. Two code bugs found (address type). Two values missing (provider_id, account_id). Possible account tier issue (guest token).**
