# Contributing to studex-app-warehouse

Welcome to the App Warehouse! 🏭

## Principles

1. **Client-first**: Every decision serves the client's outcome, not our convenience
2. **Speed matters**: We're optimising for hours, not weeks
3. **Quality is non-negotiable**: Fast delivery that breaks is worse than slow delivery that works
4. **BMAD is the process**: Follow the BMAD workflow for all new builds

## Getting Started

```bash
git clone https://github.com/TumeloRamaphosa/studex-app-warehouse.git
cd studex-app-warehouse
npm install
```

## Adding a New Template

1. Create `templates/[template-name]/`
2. Add `template-manifest.json` (name, stack, features, estimated hours)
3. Scaffold the full project (Next.js, React Native, etc.)
4. Add a `templates/[template-name]/README.md`
5. Update `docs/template-guide.md`
6. Test the full BMAD pipeline end-to-end

## Template Quality Checklist

Before a template is added to the live library:
- [ ] Project builds without errors (`npm run build`)
- [ ] Environment variables documented in `.env.example`
- [ ] README with setup instructions
- [ ] Tested on staging deployment
- [ ] CodeRabbit review passed
- [ ] Sign-off from CTO

## Running BMAD for a Client App

```bash
npm run launch-app -- --client="Acme Butchery" --type=restaurant
```

See `docs/client-onboarding.md` for full onboarding flow.

## Pull Request Process

1. Branch: `template/`, `docs/`, `workflow/`
2. Include demo screenshots/GIFs in PR
3. Document any new env vars
4. Run `npm run templates:validate` before submitting

## Status Labels

- 🔴 **Planning** — Not yet started
- 🟡 **In Progress** — Active development
- 🟢 **Live** — Available for client use
