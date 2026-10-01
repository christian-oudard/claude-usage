---
name: usage
description: Check the Anthropic subscription usage limits. Use this to check how much of the quota your work is using.
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/check_usage.py*)
---

Run exactly this command:

```
${CLAUDE_SKILL_DIR}/check_usage.py
```

The quota is shared. Other agents and sessions on this account, and the user's own chats,
draw from the same limits.

To estimate what your work costs, check before and after a chunk of work and compare the
percent used. The change includes other agents' usage, so account for this. Percent used
is a whole number, so measure over chunks of work big enough to move it by at least 1%.

If, at the current rate, a limit would run out before it resets:
- Tell the user the numbers: percent used, the rate, and when it would run out.
- Use less: cheaper models for subagents, fewer subagents in parallel, less rereading of
  large files and outputs.
- Finish the current step and stop at a clean checkpoint, not mid-change.
- Don't start large new work without the user's go-ahead.

Check at milestones, not in a loop: the endpoint allows about 3 checks a minute, and going
over the rate limit locks out every agent for 5 minutes. If it fails, report the error and
don't guess the quota.
