---
name: optimizing-aso-metadata
description: Use when researching or rewriting Google Play and App Store metadata for ASO, especially titles, subtitles, keywords, descriptions, screenshots, competitor sets, Sensor Tower exports, and platform policy compliance.
---

# Optimizing ASO Metadata

## Overview

Use this skill for evidence-backed ASO work on Apple App Store and Google Play.

Default posture:

- separate evidence from inference
- export raw data before summarizing
- separate direct competitors from broad category leaders
- draft store-specific metadata, not one blended version
- run a compliance pass before presenting copy

Read these files as needed:

- `references/methodology.md` for the working ASO model
- `references/data-requirements.md` for required inputs and export structure
- `references/policies.md` before writing or reviewing metadata
- `references/competitor-snapshot.md` for a concrete Sensor Tower-backed example

If Sensor Tower is relevant, also use [sensortower-research](../sensortower-research/SKILL.md).

## Workflow

### 1. Resolve scope first

Confirm or infer:

- target app, store, country, and locale
- whether this is launch, relaunch, localization, or rewrite
- north-star metric: search visibility, install CVR, organic installs, ranking defense, or policy-safe cleanup

Build a competitor pool with three buckets:

1. direct JTBD competitors
2. category leaders
3. adjacent substitutes

Do not rely on category leaders alone for copy decisions.

### 2. Build the evidence base

Collect the smallest useful set of raw inputs:

- existing metadata and screenshots
- current description, changelog, privacy policy, permissions, pricing, and paywall model
- a permission-to-feature matrix for every sensitive permission the app declares or might need, to be included in the final ASO document
- if the app requires login, a reviewer-safe test account plus exact login steps for Google Play review
- competitor store pages
- Sensor Tower exports when scale, keyword, ranking, or review evidence matters

Prefer raw exports in the current workspace before analysis.

Typical Sensor Tower sequence:

```bash
python3 /Users/jerryhu/.codex/skills/sensortower-research/scripts/sensortower_cli.py search --term "photo cleaner" --store unified --entity-type app --records-only
python3 /Users/jerryhu/.codex/skills/sensortower-research/scripts/sensortower_cli.py metadata --os ios --app-id 1583884012 --country US --output ./research/ios-app.json
python3 /Users/jerryhu/.codex/skills/sensortower-research/scripts/sensortower_cli.py sales --os ios --app-id 1583884012 --country WW --date-granularity monthly --start-date 2026-01-01 --end-date 2026-02-28 --output ./research/ios-sales.json
python3 /Users/jerryhu/.codex/skills/sensortower-research/scripts/sensortower_cli.py keywords --os ios --app-id 1583884012 --country US --output ./research/ios-keywords.json
python3 /Users/jerryhu/.codex/skills/sensortower-research/scripts/sensortower_cli.py keyword-research --os ios --term "photo cleaner" --country US --app-id 1583884012 --output ./research/kw-photo-cleaner.json
```

Use `top-apps` or `rankings` to discover category leaders. Use `reviews`, `review-summary`, and `ratings` when the task involves tone, claims, positioning, or trust.

### 3. Analyze before drafting

Create a short structured memo before writing copy:

- product job-to-be-done
- feature proof points that are actually shipped
- permission proof points: which feature needs which permission, and what fallback exists if the user declines
- search-intent buckets
- keyword gaps vs direct competitors
- screenshot and first-screen message gaps
- risky claims that need verification

Prefer this framing:

- P0: must-win exact intent terms
- P1: strong related terms
- P2: long-tail or scenario terms
- P3: experimental or localization-specific terms
- blocked: irrelevant, risky, or policy-sensitive terms

### 4. Draft by store, not by habit

Apple and Google Play have different fields and search behavior. Draft separately.

For Apple:

- treat app name, subtitle, keywords, screenshots, and first sentence as the highest-value metadata surface
- do not use promotional text as a keyword dump
- keep screenshots tightly aligned with the in-app experience

For Google Play:

- optimize app name, short description, full description, screenshots, and feature graphic together
- write naturally but keep core intent terms early and clearly
- avoid repetitive or irrelevant keyword stuffing

### 5. Run a compliance pass

Before presenting final copy, verify:

- every claim maps to a real feature
- privacy, offline, security, and AI claims match actual behavior and policy declarations
- every sensitive permission maps to a user-facing feature with a clear necessity statement
- the app requests the minimum permission scope and has a less-invasive fallback when policy expects one
- if login gates any content, the final ASO document includes a reusable test account and step-by-step access instructions for Google Play reviewers
- screenshots and previews show the real app experience
- pricing, IAP, ads, and subscriptions are not hidden or misrepresented
- competitor names, trademarks, rankings, and irrelevant phrases are not used to game search
- `What's New` or release notes are specific when the change is material

If any claim cannot be verified, remove it or mark it as blocked.

### 6. Deliverables

Default deliverables:

1. one final ASO document that includes competitor evidence, keyword inventory, metadata recommendations, permission-to-feature mapping, login test access details when applicable, and compliance risks
2. one to three copy variants per store if rewriting is requested

## Do Not

- do not treat category-top apps as automatic direct competitors
- do not write one blended description for both stores
- do not invent keyword volume, rank, or growth numbers
- do not claim privacy, offline processing, or AI capabilities that are not clearly supported
- do not add trademarked terms, competitor names, or promotional pricing language to metadata just to capture traffic
- do not create a separate permissions markdown file; keep permission analysis inside the final ASO document
- do not omit test credentials or reviewer steps when login, membership, region lock, or any other access gate exists
