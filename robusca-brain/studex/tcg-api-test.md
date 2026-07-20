# TCG ShipLogic API Test Results

**Date:** 2026-03-12  
**Script:** `/workspace/scripts/tcg-bulk-delivery.py`  
**CSV Source:** `/workspace/studex/tcg-delivery-template.csv`  
**Test Row:** Row 1 — John Dlamini, 12 Main Road, Sandton, Johannesburg, Gauteng, 2196

---

## 1. Endpoint Discovery

Both base URLs were probed:

| Base URL | GET /shipments Response |
|----------|------------------------|
| `https://api.shiplogic.com/v2` | ✅ Responds (auth required) |
| `https://api.shiplogic.com` | ✅ Responds (auth required) |

**Working base URL:** `https://api.shiplogic.com/v2`

---

## 2. Authentication Method Testing

All common auth formats were tested against `GET /v2/shipments`:

| Auth Header Format | HTTP Status | Response |
|-------------------|-------------|----------|
| `Authorization: Bearer {full_key}` | **401** | `Authentication failed, please check your API key.` |
| `Authorization: Bearer {token_only}` | **401** | `Authentication failed, please check your API key.` |
| `Authorization: Token {full_key}` | **403** | `{"message":"You do not have permission to view shipments (not_logged_in)"}` |
| `X-API-Key: {full_key}` | **403** | `{"message":"You do not have permission to view shipments (not_logged_in)"}` |
| `Api-Key: {full_key}` | **403** | `{"message":"You do not have permission to view shipments (not_logged_in)"}` |
| Query param `?api_key={full_key}` | **403** | `{"message":"You do not have permission to view shipments (not_logged_in)"}` |

**Key finding:** `Bearer` gives a clean 401 "check your API key" → definitive auth failure.  
`Token` / `X-API-Key` give 403 "not_logged_in" — the server recognises the credential format but the account context is missing.

---

## 3. Shipment Creation Test (POST /v2/shipments)

Full payload was submitted for John Dlamini using `Token` auth (the most permissive format):

### Payload Sent

```json
{
  "collection_address": {
    "type": "building",
    "company": "Studex Meat (Pty) Ltd",
    "street_address": "19 Pomona Rd",
    "local_area": "Pomona AH",
    "city": "Kempton Park",
    "zone": "GAU",
    "country": "ZA",
    "code": "1623"
  },
  "collection_contact": {
    "name": "Eugene",
    "mobile_number": "+27792438740",
    "email": "Deli@noags.co.za"
  },
  "delivery_address": {
    "type": "building",
    "company": "",
    "street_address": "12 Main Road",
    "local_area": "Sandton",
    "city": "Johannesburg",
    "zone": "GAU",
    "country": "ZA",
    "code": "2196"
  },
  "delivery_contact": {
    "name": "John Dlamini",
    "mobile_number": "+27821234567",
    "email": "john@email.com"
  },
  "parcels": [
    {
      "submitted_length_cm": 30,
      "submitted_width_cm": 48,
      "submitted_height_cm": 17,
      "submitted_weight_kg": 3
    }
  ],
  "service_level": { "code": "ECO" },
  "declared_value": 150.0,
  "special_instructions_collection": "",
  "special_instructions_delivery": ""
}
```

### Response

| Method | Endpoint | Status | Response Body |
|--------|----------|--------|---------------|
| `POST` | `/v2/shipments` (Bearer) | **401** | `Authentication failed, please check your API key.` |
| `POST` | `/v2/shipments` (Token) | **400** | `could not create shipment: provider_id invalid` |

---

## 4. Waybill Created?

**No waybill was created.** The API authentication is not fully resolving.

---

## 5. Root Cause Analysis

### Most Likely Issues

1. **API key may be expired or belong to a different environment (staging vs production).**  
   The key `53612520|d2l9DRSecZr2Ikh3SdlR5TOy8sWIZaYJiMnTL2XM9b2f0246` follows Laravel Sanctum format (`{token_id}|{secret}`). The `Bearer` prefix is the correct format for Sanctum tokens — the 401 "check your API key" suggests the key itself is not recognised by the production API.

2. **`Token` prefix auth reaches payload validation** (gets a 400 instead of 401), but the account it resolves to is not linked to a ShipLogic carrier provider (`provider_id invalid`). This may mean a different API key type is being used.

3. **Account setup incomplete:** The ShipLogic account may need carrier/provider configuration completed in the portal before shipments can be created via API.

---

## 6. Recommended Actions for Agent Lord

1. **Log in to ShipLogic portal** → Settings → API Keys → verify the key is still active and copy the exact key as shown.
2. **Check if the account has a carrier (provider) configured** — the `provider_id invalid` error means no default courier is linked to the account.
3. **Confirm the API base URL** — some accounts use `https://api.shiplogic.com/v2`, others may use a reseller subdomain.
4. **Once auth is confirmed,** run: `python3 /workspace/scripts/tcg-bulk-delivery.py --test`

---

## 7. Script Status

The script is **fully written and ready** at `/workspace/scripts/tcg-bulk-delivery.py`.

### What it does (once auth works):
- ✅ Reads CSV from `/workspace/studex/tcg-delivery-template.csv`
- ✅ Maps Province names → ShipLogic zone codes (GAU/WC/KZN/EC/LIM/MP/NW/FS/NC)
- ✅ Normalises SA phone numbers (08x → +27x)
- ✅ POSTs full ShipLogic v2 shipment payload per row
- ✅ Downloads waybill PDF via `/v2/shipments/{id}/label`
- ✅ Saves PDFs to `/workspace/studex/waybills/waybill_001_John_Dlamini.pdf` etc.
- ✅ No external dependencies (pure Python stdlib — `urllib`, `csv`, `json`)

### Usage
```bash
# Test first row only
python3 /workspace/scripts/tcg-bulk-delivery.py --test

# Process all rows
python3 /workspace/scripts/tcg-bulk-delivery.py

# Process specific row (e.g., row 2)
python3 /workspace/scripts/tcg-bulk-delivery.py --row 2
```

---

## 8. Auth Format in Script

The script currently uses `Authorization: Token {API_KEY}` (gets furthest in testing).  
Change line in script if ShipLogic confirms correct format:
```python
# Line ~37 in tcg-bulk-delivery.py
"Authorization": f"Token {API_KEY}",   # current
"Authorization": f"Bearer {API_KEY}",  # try this if Token fails after account fix
```
