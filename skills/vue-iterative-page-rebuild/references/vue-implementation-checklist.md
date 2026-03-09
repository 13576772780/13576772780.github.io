# Vue Implementation Checklist

Run this checklist on every round.

## Before coding

- Confirm current target: desktop/mobile/both.
- Confirm screenshot viewport and DPR are fixed.
- Confirm `layout.json` component map matches current Vue component names.

## During coding

- Keep changes minimal and issue-oriented.
- Fix `high` before `medium`, `medium` before `low`.
- Update only related `.vue` / style files.
- Avoid unrelated refactor or rename.

## Before screenshot

- Ensure fonts are loaded.
- Wait for async content to settle.
- Hide transient animations if they affect comparison.

## After screenshot

- Record round score and unresolved issues.
- Detect regressions from previously solved high issues.
- Decide continue/stop using stop script.
