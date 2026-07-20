# Data Models

## Supabase Tables
- orders: id, shopify_id, customer_id, status, total, tracking_number
- inventory: id, product_id, variant_id, quantity, updated_at
- fulfilments: id, order_id, packer_id, status, dispatched_at
- naledi_content: id, platform, content, status, scheduled_at
