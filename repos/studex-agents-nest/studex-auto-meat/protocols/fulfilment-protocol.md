# Fulfilment Standard Operating Procedure

## Order Lifecycle
1. Shopify `order/create` webhook fires
2. HMAC signature verified
3. Order saved to Supabase `orders` table
4. Inventory check against `inventory` table
5. If sufficient: mark `status=confirmed`, assign packer
6. Packer marks fulfilled → `fulfillment/create` webhook
7. Tracking number saved → pushed to Shopify
8. Customer notified via WhatsApp

## Escalation Rules
- Low stock → flag for manual review (do not auto-fulfil)
- Payment failed → mark `status=payment_failed`, alert team
- Missing address → mark `status=needs_review`
