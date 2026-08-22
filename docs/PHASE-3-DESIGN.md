# Phase 3 design

## Goal

Expand the idea layer and the deterministic build layer without changing the Phase 2 contract: each scheduled run must select one not-yet-built idea, render the matching static template, validate it, publish it under a unique weekly path, and notify Telegram.

## Idea backlog schema

Ideas will live in `ideas/backlog.json` as versioned records with `id`, `slug`, `title`, `pitch`, `strategy`, `status`, `difficulty`, and `category`. The `strategy` field is required and maps to one deterministic template. Valid statuses are `backlog`, `built`, and `retired`. The picker only considers `backlog` records and writes `built_period` when it marks a record as built.

## Tier A template map

| Strategy tag | Shape | Template |
|---|---|---|
| `template:idea-mashup` | Idea generator | Existing `products/idea-mashup/index.html` |
| `template:converter` | Converter | `templates/converter.html` |
| `template:visual-toy` | Small visual toy | `templates/visual-toy.html` |
| `template:text-tool` | Text tool | `templates/text-tool.html` |

Each template is a standalone HTML file with inline CSS and JavaScript. No template may require a backend, an external library, a remote asset, or an external API.

## Picker behavior

The picker uses a SHA-256 hash of the ISO week period to choose a stable index among currently available backlog records. It then marks the selected record `built` with the period and emits a JSON selection file for the builder. If no backlog record remains, the workflow fails clearly instead of repeating an already built idea.

## Compatibility behavior

The Phase 2 weekly workflow will be upgraded to call the picker and pass the selected idea to the builder. Existing Phase 1 and Phase 2 products remain untouched. The weekly artifact path remains `products/weekly/YYYY-wNN/`, while the selected idea and strategy determine the rendered template.

## Gate criteria

Phase 3 is complete when the backlog is versioned, at least three additional deterministic templates exist, the picker marks ideas without repetition, every template passes local validation, and a manual weekly run successfully publishes one newly selected product and sends its Telegram notification. Phase 4, LLM generation, and provider fallback remain out of scope.
