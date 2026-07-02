# Google Maps Routes API Integration — Delivery ETA Engine

**Spec version:** 1.0.0  
**Date:** 2026-06-29  
**Author:** Robusca (Delivery B@ye integrations layer)

---

## Overview

The Delivery Agent uses the **Google Maps Routes API** to calculate accurate,
traffic-aware ETAs for each delivery. The API is called after an order is
assigned to a driver and before the dispatch WhatsApp is sent to the customer.

**Primary API:** Google Maps Routes API v2 (`computeRoutes`)  
**Fallback:** Haversine straight-line distance estimate (no API key required)  
**Free tier:** 28,000 calls/month — sufficient for a SA meat delivery business

---

## Google Maps Routes API — v2

### Endpoint
```
POST https://routes.googleapis.com/directions/v2:computeRoutes
```

### Required Headers

| Header | Value |
|---|---|
| `X-Goog-Api-Key` | `${GOOGLE_MAPS_API_KEY}` |
| `X-Goog-FieldMask` | `routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline` |
| `Content-Type` | `application/json` |

### Request Body Template

```json
{
  "origin": {
    "address": "190 Rooiberg St, N4 Gateway Park, The Willows, Pretoria, Gauteng, South Africa"
  },
  "destination": {
    "address": "14 Kingsway Ave, Sandton, Johannesburg, Gauteng, 2196, South Africa"
  },
  "intermediates": [],
  "travelMode": "DRIVE",
  "routingPreference": "TRAFFIC_AWARE",
  "departureTime": "2026-06-29T12:00:00+02:00",
  "computeAlternativeRoutes": false,
  "routeModifiers": {
    "avoidTolls": false,
    "avoidHighways": false,
    "avoidFerries": false
  },
  "languageCode": "en-ZA",
  "units": "METRIC"
}
```

### Response Shape

```json
{
  "routes": [
    {
      "distanceMeters": 28450,
      "duration": "PT45M30S",
      "polyline": {
        "encodedPolyline": "_p~iF~ps|U_ulLnnqC_mqNvxq`@"
      }
    }
  ]
}
```

**Field extraction:**
- `distance_meters` = `routes[0].distanceMeters`
- `duration_seconds` = parse ISO 8601 duration `routes[0].duration` → e.g. `PT45M30S` → `45*60 + 30 = 2730`
- `duration_human` = `"45 mins"` (formatted from seconds)
- `eta_actual` = `departureTime + duration`

---

## Routing Origin Points

Use the warehouse/supplier closest to the destination:

| Origin | Address | Use for |
|---|---|---|
| **Silent Valley depot** | 190 Rooiberg St, N4 Gateway Park, The Willows, Pretoria | Orders sourced from Silent Valley |
| **Noags Butchery** | 19 Pomona Rd, Pomona AH, Kempton Park, 1623 | Orders sourced from Noags |
| **Moutloe Farm** | From product data | Orders with Moutloe provenance |

In practice, for most JHB metro deliveries the origin is:
**19 Pomona Rd, Pomona AH, Kempton Park, 1623** (central Gauteng depot)

---

## Response Parsing (Node.js)

```js
/**
 * Parse Google Maps Routes API v2 response into ETA object.
 * @param {object} response - Axios HTTP response data
 * @returns {object} { distance_meters, duration_seconds, eta_actual: Date }
 */
function parseRoutesResponse(response) {
  const route = response.routes?.[0];
  if (!route) throw new Error('No routes returned from Google Maps API');

  const distanceMeters = route.distanceMeters ?? 0;

  // Parse ISO 8601 duration: PT45M30S → seconds
  const durationStr = route.duration ?? 'PT0S';
  const match = durationStr.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
  const hours = parseInt(match?.[1] ?? 0);
  const minutes = parseInt(match?.[2] ?? 0);
  const seconds = parseInt(match?.[3] ?? 0);
  const durationSeconds = hours * 3600 + minutes * 60 + seconds;

  // ETA = now (or departureTime if provided) + duration
  const baseTime = new Date();
  const etaActual = new Date(baseTime.getTime() + durationSeconds * 1000);

  return {
    distance_meters: distanceMeters,
    distance_km: (distanceMeters / 1000).toFixed(1),
    duration_seconds: durationSeconds,
    duration_human: formatDuration(durationSeconds),
    eta_actual: etaActual.toISOString(),
    eta_human: etaActual.toLocaleTimeString('en-ZA', {
      timeZone: 'Africa/Johannesburg',
      hour: '2-digit',
      minute: '2-digit',
    }),
  };
}

function formatDuration(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 0) return `${h}h ${m}m`;
  return `${m} mins`;
}
```

---

## Complete ETA Calculation Function

```js
const axios = require('axios');

const GOOGLE_MAPS_API_KEY = process.env.GOOGLE_MAPS_API_KEY;
const ROUTES_API_URL = 'https://routes.googleapis.com/directions/v2:computeRoutes';

/**
 * Calculate delivery ETA for a given order.
 * @param {object} order - Order object from delivery-state.json
 * @param {string} originAddress - Depot/supplier address
 * @returns {Promise<object>} ETA result
 */
async function calculateDeliveryETA(order, originAddress) {
  const destinationAddress = order.customer.address;

  // ── Attempt 1: Google Maps Routes API ──────────────────────────────────
  if (GOOGLE_MAPS_API_KEY) {
    try {
      const response = await axios.post(
        ROUTES_API_URL,
        {
          origin: { address: originAddress },
          destination: { address: destinationAddress },
          travelMode: 'DRIVE',
          routingPreference: 'TRAFFIC_AWARE',
          departureTime: new Date().toISOString(),
          computeAlternativeRoutes: false,
          routeModifiers: {
            avoidTolls: false,
            avoidHighways: false,
            avoidFerries: false,
          },
          languageCode: 'en-ZA',
          units: 'METRIC',
        },
        {
          headers: {
            'X-Goog-Api-Key': GOOGLE_MAPS_API_KEY,
            'X-Goog-FieldMask':
              'routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline',
            'Content-Type': 'application/json',
          },
          timeout: 8000,
        }
      );

      const eta = parseRoutesResponse(response.data);
      return {
        ...eta,
        method: 'google_maps_routes_api',
        origin: originAddress,
        destination: destinationAddress,
      };
    } catch (err) {
      console.warn(
        `[ETA] Google Maps API failed for order ${order.order_number}: ${err.message}`
      );
      // Fall through to fallback
    }
  }

  // ── Fallback: Haversine straight-line estimate ──────────────────────────
  console.warn(`[ETA] Using straight-line fallback for order ${order.order_number}`);
  return estimateETAFallback(originAddress, destinationAddress, order.order_number);
}

/**
 * Straight-line ETA fallback using Haversine distance + average SA speed.
 */
async function estimateETAFallback(originAddress, destinationAddress, orderNumber) {
  if (GOOGLE_MAPS_API_KEY) {
    try {
      const [originCoords, destCoords] = await Promise.all([
        geocodeAddress(originAddress),
        geocodeAddress(destinationAddress),
      ]);

      const distanceMeters = haversineDistance(
        originCoords.lat, originCoords.lng,
        destCoords.lat, destCoords.lng
      );

      const distanceKm = distanceMeters / 1000;
      // Conservative SA urban average speed: 40 km/h
      const durationSeconds = Math.round((distanceKm / 40) * 3600);
      const etaActual = new Date(Date.now() + durationSeconds * 1000);

      return {
        distance_meters: Math.round(distanceMeters),
        distance_km: distanceKm.toFixed(1),
        duration_seconds: durationSeconds,
        duration_human: formatDuration(durationSeconds),
        eta_actual: etaActual.toISOString(),
        eta_human: etaActual.toLocaleTimeString('en-ZA', {
          timeZone: 'Africa/Johannesburg',
          hour: '2-digit',
          minute: '2-digit',
        }),
        method: 'haversine_fallback',
        origin: originAddress,
        destination: destinationAddress,
      };
    } catch (err) {
      console.error(`[ETA] Geocoding fallback failed for order ${orderNumber}: ${err.message}`);
    }
  }

  // ── Last resort: rough zone-based estimate ────────────────────────────
  return {
    distance_meters: null,
    distance_km: null,
    duration_seconds: null,
    duration_human: 'TBD — confirm with driver',
    eta_actual: null,
    eta_human: 'TBD',
    method: 'zone_estimate',
    origin: originAddress,
    destination: destinationAddress,
  };
}

function haversineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371000; // Earth radius in metres
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function toRad(deg) {
  return deg * (Math.PI / 180);
}

async function geocodeAddress(address) {
  const response = await axios.get(
    'https://maps.googleapis.com/maps/api/geocode/json',
    {
      params: { address, key: GOOGLE_MAPS_API_KEY },
      timeout: 5000,
    }
  );
  const result = response.data.results?.[0];
  if (!result) throw new Error(`Geocoding failed for: ${address}`);
  return result.geometry.location;
}

function parseRoutesResponse(data) {
  const route = data.routes?.[0];
  if (!route) throw new Error('No routes returned from Google Maps API');

  const distanceMeters = route.distanceMeters ?? 0;
  const durationStr = route.duration ?? 'PT0S';
  const match = durationStr.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
  const hours = parseInt(match?.[1] ?? 0);
  const minutes = parseInt(match?.[2] ?? 0);
  const seconds = parseInt(match?.[3] ?? 0);
  const durationSeconds = hours * 3600 + minutes * 60 + seconds;

  const etaActual = new Date(Date.now() + durationSeconds * 1000);

  return {
    distance_meters: distanceMeters,
    distance_km: (distanceMeters / 1000).toFixed(1),
    duration_seconds: durationSeconds,
    duration_human: formatDuration(durationSeconds),
    eta_actual: etaActual.toISOString(),
    eta_human: etaActual.toLocaleTimeString('en-ZA', {
      timeZone: 'Africa/Johannesburg',
      hour: '2-digit',
      minute: '2-digit',
    }),
  };
}

function formatDuration(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 0) return `${h}h ${m}m`;
  return `${m} mins`;
}
```

---

## Geocoding API (Supporting Endpoint)

Before calling `computeRoutes`, the Delivery Agent may need to geocode
customer addresses (if they are stored as free text and need lat/lng):

```
GET https://maps.googleapis.com/maps/api/geocode/json
  ?address=14+Kingsway+Ave,+Sandton,+Johannesburg,+South+Africa
  &key=${GOOGLE_MAPS_API_KEY}
```

Response:
```json
{
  "results": [
    {
      "geometry": {
        "location": { "lat": -26.1076, "lng": 28.0567 }
      },
      "formatted_address": "14 Kingsway Ave, Sandton, 2196, South Africa"
    }
  ],
  "status": "OK"
}
```

---

## ETA Urgency Colour Coding (Kanban Display)

| Condition | Colour | Label |
|---|---|---|
| ETA > 2 hours away | 🟢 Green | "On track" |
| ETA 1–2 hours away | 🟡 Yellow | "Soon" |
| ETA < 1 hour away | 🔴 Red | "Imminent" |
| ETA missed by >30 min | ⚠️ Alert | "DELAYED — escalate to Robusca" |

---

## Caching Strategy

To minimise API calls (preserve the 28k/month free tier):

| Cache target | Key | TTL | Store |
|---|---|---|---|
| Geocoded address → lat/lng | SHA256(normalised_address) | 30 days | `/workspace/studex-os/cache/geocode/` |
| Route result | SHA256(origin + destination) | 1 hour | `/workspace/studex-os/cache/routes/` |

```js
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

function cacheGet(cacheDir, key) {
  const file = path.join(cacheDir, `${key}.json`);
  if (!fs.existsSync(file)) return null;
  const { value, expiresAt } = JSON.parse(fs.readFileSync(file, 'utf8'));
  if (Date.now() > expiresAt) { fs.unlinkSync(file); return null; }
  return value;
}

function cacheSet(cacheDir, key, value, ttlMs) {
  const file = path.join(cacheDir, `${key}.json`);
  fs.mkdirSync(cacheDir, { recursive: true });
  fs.writeFileSync(file, JSON.stringify({ value, expiresAt: Date.now() + ttlMs }));
}

function addressCacheKey(address) {
  return crypto.createHash('sha256').update(address.toLowerCase().trim()).digest('hex');
}
```

---

## Environment Variables

```
GOOGLE_MAPS_API_KEY=   # From Google Cloud Console — Maps JavaScript + Routes API + Geocoding API enabled
```

---

## Google Cloud Console Setup Checklist

1. Go to https://console.cloud.google.com
2. Create project "Studex Meat" (or select existing)
3. Enable: **Routes API**, **Maps JavaScript API**, **Geocoding API**
4. Credentials → Create API Key → apply HTTP restrictions:
   - Referrer: `*.studexmeat.com/*`
   - IP: restrict to Orgo VM IP `67.213.119.157`
5. Set quota: 28,000 requests/month (Routes API quota)
6. Share key with Robusca to add to Charlie env

---

## Error Handling

| Error | Action |
|---|---|
| API key missing | Use Haversine fallback silently |
| API returns `ZERO_RESULTS` | Log, use fallback, alert Robusca |
| API returns `OVER_QUERY_LIMIT` | Wait 2s, retry once; if still fail → fallback |
| API timeout (>8s) | Fallback immediately, log warning |
| Network unreachable | Fallback, log error |
| Geocoding fails | Skip geocode cache miss, try Routes API with address string directly |

---

## Implementation Checklist

- [ ] Get Google Maps API key from Tumelo
- [ ] Enable Routes API + Geocoding API in Google Cloud Console
- [ ] Set API key in Charlie `.env` as `GOOGLE_MAPS_API_KEY`
- [ ] Implement `calculateDeliveryETA()` in Delivery Agent
- [ ] Add file-based cache for geocoding and routes
- [ ] Wire ETA result into Kanban card and WhatsApp messages
- [ ] Test end-to-end with a real JHB address
- [ ] Verify fallback works when API key is absent
