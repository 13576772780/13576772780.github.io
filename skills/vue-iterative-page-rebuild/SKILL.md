---
name: vue-iterative-page-rebuild
description: Build and refine a Vue web page to match a target screenshot using iterative visual feedback in Claude Code. Use when tasks mention target image + layout JSON, screenshot comparison, multimodal review output, or multi-round patching for Vue projects.
---

# Vue Iterative Page Rebuild

Use this workflow to implement and iteratively refine a Vue page from `target.png` and `layout.json`.

## Execute Workflow

1. Validate inputs: ensure `target.png`, `layout.json`, and project run command are known.
2. Generate initial Vue implementation from `layout.json` and target image description.
3. Run the app and capture deterministic screenshot (`current.png`).
4. Compare `target.png` and `current.png` with multimodal model; save structured output to `review.json`.
5. Build a minimal patch prompt from `review.json` (Top-K issues, high first).
6. Apply patch only to related Vue files.
7. Repeat until stop conditions are met.

## Enforce Output Contract

Require multimodal review to output strict JSON with fields:

- `global_score`
- `layout_similarity`
- `style_similarity`
- `issues[]` with `id`, `severity`, `category`, `component`, `description`, `suggestion`
- `next_actions[]`

Reject non-JSON output and rerun review.

## Apply Vue-Specific Rules

- Keep SFC structure clear: `template` for structure, `script setup` for logic, `scoped style` for local styles.
- Prefer tokenized spacing and typography variables in global styles.
- Patch incrementally; avoid full component rewrites unless structure is wrong.
- Keep DOM selectors stable for screenshot testing (`data-testid` when needed).

## Use Bundled Resources

- Read `references/review-schema.md` for JSON schema and severity mapping.
- Read `references/vue-implementation-checklist.md` before each patch round.
- Reuse `assets/templates/*.md` prompt templates directly.
- Run `scripts/build_patch_prompt.py` to convert `review.json` to a focused patch prompt.
- Run `scripts/evaluate_stop.py` to decide whether to continue iteration.

## Stop Conditions

Stop when any condition is true:

- `global_score >= 0.92`
- Max rounds reached (default 10)
- Improvement < `0.01` over last 2 rounds

If stopped by convergence or max rounds, produce remaining high-priority issues for manual review.
