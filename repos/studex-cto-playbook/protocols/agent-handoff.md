# Agent Handoff Protocol

When one agent passes context to another:
1. Write session summary to shared memory file
2. Include: what was done, pending tasks, key context
3. Next agent reads summary before starting
4. Use consistent naming: `memory/YYYY-MM-DD/[agent-name].md`
