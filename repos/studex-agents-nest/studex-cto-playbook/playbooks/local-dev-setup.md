# Local Dev Setup

## Requirements
- Node.js 20+
- Docker (for Supabase local)
- ngrok (for webhook testing)
- Git

## Setup
```bash
git clone https://github.com/TumeloRamaphosa/studex-cto-playbook.git
cd studex-cto-playbook
npm install -g @supabase/cli
supabase init
supabase start
cp .env.example .env
```
