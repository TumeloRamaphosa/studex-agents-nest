# Shopify Integration

## Setup
1. Create private app in Shopify Admin
2. Grant: orders, products, fulfillments, inventory scopes
3. Copy Admin API access token

## Webhooks Required
- orders/create
- orders/paid
- fulfillments/create

## API Rate Limits
- 40 requests/second (burst), 2 requests/second (sustained)
