# Q-RoPE Transfer Family Selection Decision v1

Date: 2026-03-12
Stories: S960

## Decision
- use the preserved/archived transfer portfolio as a selection filter for future transfer lines
- do not open new transfer execution by default
- require memo-level survivability screening before any future transfer approval candidate is allowed

## Why
- the portfolio is now strong enough to support a theory-backed selection rule
- the `braid` archive gives the line a concrete negative boundary
- more transfer execution without this filter would likely restart branch sprawl
