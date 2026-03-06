# Checkpoint system

## Purpose
Maintain a lightweight source of truth for current state so work can resume cleanly across sessions.

## Canonical location
Store the checkpoint in `logs/checkpoint.json`.

## When to update
- Start of each session.
- Before each major action.
- After story status changes.
- Before ending a session.

## Required fields
`logs/checkpoint.json` must include:
- `timestamp_utc`
- `current_epic_id`
- `current_epic_title`
- `current_epic_status`
- `current_story_ids`
- `active_workers`
- `next_actions`
- `risks_or_blocks`

## Optional fields
- `last_test_run`
- `recent_changes`
- `notes`
- `planning_loop`
