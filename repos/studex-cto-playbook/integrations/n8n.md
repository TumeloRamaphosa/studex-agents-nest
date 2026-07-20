# N8n Workflow Setup

## Self-hosted
docker run -d --name n8n -p 5678:5678 n8nio/n8n

## Key Workflows
- Client intake → triggers Warehouse Agent
- Content approval → notifies manager
- Order dispatch → updates customer
