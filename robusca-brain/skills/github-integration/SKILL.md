# GitHub Integration Skill — Robusca
# Agent Lord: TumeloRamaphosa
# Configured: 2026-03-12

## Connected Account
- Username: TumeloRamaphosa
- Token: stored in /workspace/.github-config
- API Base: https://api.github.com
- Auth Header: Authorization: Bearer <token>

## Existing Repositories
1. TumeloRamaphosa (profile repo) — HTML
2. distributed_exchange_truffle_class_3 — Distributed exchange, JS
3. Stud-Ex-Global-Markets- — TypeScript ← MAIN BUSINESS REPO
4. SGM-NLMK — SGM + NLMK Data Analysis, HTML
5. Stud-Ex-Global-Markets-Pulsar-Oracle- — HTML
6. SGM-Pulsar-1 — SGM + Pulsar 1, HTML

## Key Repos to Create (Pending)
- studex-auto-meat (automation pipeline)
- studex-naledi-content (Naledi content assets + workflows)
- studex-app-warehouse (client app factory templates)
- studex-cto-playbook (BMAD + coding standards)

## How to Use GitHub API (no exec needed)
All GitHub operations use REST API with Bearer token authentication.

### Create a repository:
POST https://api.github.com/user/repos
{
  "name": "repo-name",
  "description": "description",
  "private": false,
  "auto_init": true
}

### Create/update a file:
PUT https://api.github.com/repos/TumeloRamaphosa/{repo}/contents/{path}
{
  "message": "commit message",
  "content": "<base64 encoded content>"
}

### Create an issue:
POST https://api.github.com/repos/TumeloRamaphosa/{repo}/issues
{
  "title": "Issue title",
  "body": "Description",
  "labels": ["bug", "enhancement"]
}

## BMAD Integration
Each new client project from the App Warehouse gets:
1. New repo created via GitHub API
2. BMAD workflow files pushed to repo
3. CodeRabbit activated on the repo
4. GitHub Actions CI/CD configured
