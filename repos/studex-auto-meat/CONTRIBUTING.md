# Contributing to studex-auto-meat

Thank you for contributing to the Studex Meat auto-fulfilment system.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/<your-username>/studex-auto-meat.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Install dependencies: `npm install`
5. Copy `.env.example` to `.env` and fill in test credentials

## Development Setup

```bash
# Use ngrok or similar for local webhook testing
ngrok http 3000

# Register webhooks pointing to your ngrok URL
npm run setup:webhooks

# Run in development
npm run dev
```

## Code Standards

- **Formatting**: Prettier (run `npm run format`)
- **Linting**: ESLint (run `npm run lint`)
- **Types**: Use JSDoc comments for all service functions
- **Commits**: Use conventional commits (`feat:`, `fix:`, `docs:`, `chore:`)

## Testing

```bash
npm test              # Run all tests
npm run test:watch   # Watch mode
```

Always add tests for new webhook handlers and service functions.

## Pull Request Process

1. **Branch naming**: `feature/`, `fix/`, `docs/`, `refactor/`
2. **PR description**: Explain what changed and why
3. **Link to issue**: Reference any related issues
4. **Checks required before merge**:
   - All tests pass (`npm test`)
   - ESLint passes with no errors
   - Webhook signature verification tested locally

## Security Notes

- Never commit `.env` files or real credentials
- All Shopify API calls use HTTPS
- Webhook payloads are HMAC-verified before processing
- Use Supabase service role key only in server-side code

## Questions

Open an issue or reach out to the CTO Department.
