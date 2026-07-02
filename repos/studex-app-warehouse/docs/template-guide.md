# Template Creation Guide

## Steps
1. Create `templates/[name]/` folder
2. Add `template-manifest.json`
3. Scaffold the project (Next.js, React Native, etc.)
4. Add `.env.example`
5. Add `README.md` with setup instructions
6. Test BMAD pipeline end-to-end
7. Submit for CTO sign-off

## template-manifest.json fields
- name, slug, description
- stack (frontend, backend, database)
- features (array)
- estimatedHours
- priceRange
- status (planning/in-progress/live)
