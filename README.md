# claude-usage

A Claude Code skill, `usage`, that lets an agent check the current token usage and quota.

Works only in Claude Code. Requires a claude.ai subscription login
and `python3`.

## Example output

```
now Thu 2026-10-08 20:40 MDT
session (all models): 72% used, resets in 1h50m at Thu 2026-10-08 22:30, on pace to run out in 1h14m at Thu 2026-10-08 21:54
weekly (all models): 91% used, resets in 1d3h20m at Sat 2026-10-10 00:00, on pace to run out in 13h55m at Fri 2026-10-09 10:35
weekly Fable: 38% used, resets in 1d3h20m at Sat 2026-10-10 00:00, on pace for 45% by reset
```

## Install

```
$ claude plugin marketplace add christian-oudard/claude-usage
$ claude plugin install claude-usage@claude-usage
```
