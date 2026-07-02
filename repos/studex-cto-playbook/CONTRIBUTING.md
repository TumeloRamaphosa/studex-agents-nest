# Contributing to studex-cto-playbook

This is the living technical bible for the entire Studex Group. Keep it accurate, concise, and actionable.

## What Goes Here

- ✅ Architecture decisions and rationale
- ✅ System integration guides
- ✅ Agent SKILL.md definitions
- ✅ Standard operating procedures
- ✅ Deployment runbooks
- ✅ Onboarding documentation

## What Does NOT Go Here

- ❌ Customer data or PII
- ❌ Secrets, API keys, credentials
- ❌ Raw meeting notes (summarise into decisions)
- ❌ Marketing content (that's `studex-naledi-content`)

## Making Changes

### Small Changes (typos, clarifications)

1. Edit the file directly
2. PR with a clear description
3. Request CTO review

### Architecture Decisions (ADRs)

For any significant technical decision:
1. Create a new file in `decisions/ADR-XXX-descriptive-name.md`
2. Include: Context, Decision, Consequences, Alternatives Considered
3. PR requires CTO approval

### Adding Agent Skills

1. Create `agents/[agent-name]/SKILL.md`
2. Follow the SKILL.md template in `agents/_template/SKILL.md`
3. Add the skill to the agent registry in `agents/registry.md`
4. Write at least one test in `tests/`

## Style Guide

- **Markdown-first**: All docs are Markdown
- **Headings**: Use `##` for sections, `###` for subsections
- **Code blocks**: Always specify language
- **Links**: Use relative links for internal docs
- **Status badges**: Use 🟢 🟡 🔴 consistently

## Pull Request Checklist

- [ ] All links are valid (run `npm run validate:links`)
- [ ] No secrets or credentials committed
- [ ] PR description explains the "why"
- [ ] CTO has been tagged for review

## Questions

Contact the CTO Department directly.
