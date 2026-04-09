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
- treat sensitive-permission review and reviewer-access prep as first-class ASO work for Google Play, not as optional release admin
- prefer explicit verified statements such as "not required in this build" or "permission not declared" over silent omission
- use bundled policy references as a starting summary only; for policy-sensitive conclusions, always verify against live official Apple / Google documentation during the current run
- if live official docs cannot be reached, do not present policy verification as complete

Read these files as needed:

- `references/methodology.md` for the working ASO model
- `references/data-requirements.md` for required inputs and export structure
- `references/policies.md` before writing or reviewing metadata, then confirm the applicable sections against the current official online docs
- `references/competitor-snapshot.md` for a concrete Sensor Tower-backed example

If Sensor Tower is relevant, also use [sensortower-research](../sensortower-research/SKILL.md).

## Workflow

### 1. Resolve scope first

Confirm or infer:

- target app, store, country, and locale
- whether this is launch, relaunch, localization, or rewrite
- north-star metric: search visibility, install CVR, organic installs, ranking defense, or policy-safe cleanup
- which official policy surfaces must be checked live for this run, at minimum the target store's metadata rules and any permission / reviewer-access guidance touched by the app

Build a competitor pool with three buckets:

1. direct JTBD competitors
2. category leaders
3. adjacent substitutes

Do not rely on category leaders alone for copy decisions.

### 2. Build the evidence base

Collect the smallest useful set of raw inputs:

- existing metadata and screenshots
- current description, changelog, privacy policy, permissions, pricing, and paywall model
- Android and iOS permission declarations from real manifests / plist / entitlements, not just docs or dependency lists
- current official Apple / Google policy pages relevant to this submission, fetched live during the run
- a permission-to-feature matrix for every sensitive permission the app declares or might need, to be included in the final ASO document
- an explicit "permissions not declared in this build" list for common high-risk categories when preparing Google Play documentation
- if the app requires login, or if any feature likely to matter during review is auth-gated, a reviewer-safe test account plus exact login steps for Google Play review
- when the gated path uses Firebase Authentication, create or refresh the reviewer-safe account in Firebase, verify the credentials actually work in the current build, then record them in the final ASO document
- competitor store pages
- Sensor Tower exports when scale, keyword, ranking, or review evidence matters

Prefer raw exports in the current workspace before analysis.

For store-policy work, explicit internet validation is mandatory by default:

- open the bundled `references/policies.md` first to orient
- then fetch the live official Apple and/or Google source pages relevant to the target store
- base final policy conclusions on the live official pages, using the bundled summary only as a helper
- record the official pages checked, or at least the checked date and source set, in the working notes or final ASO artifact when policy risk is material

For Google Play, do not stop at "we should include reviewer credentials." Treat reviewer access as incomplete until all of the following are true:

- the gated feature set has been identified from code and routing
- the test account exists in the real auth backend
- the exact credentials have been validated against the current app build or a reviewer-equivalent environment
- the final ASO document contains the credentials, login steps, MFA / OTP notes, region prerequisites, and post-login navigation steps

If Firebase access is unavailable in the current environment, explicitly mark reviewer-account creation and login verification as a blocker rather than silently leaving placeholders.

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
- permission-negative proof points: which sensitive permissions are not declared, so they should not appear in Play explanations
- review-access proof points: whether core review flows require login, and if so which path is gated
- policy verification proof points: which live official pages were checked this run, what they confirmed, and any ambiguity that remains
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
- include review-facing documentation in the final ASO package, not only public-facing metadata
- when auth exists, add a dedicated `Google Play Review Access` section even if the answer is "not required for this build"

### 5. Run a compliance pass

Before presenting final copy, verify:

- every claim maps to a real feature
- privacy, offline, security, and AI claims match actual behavior and policy declarations
- policy-sensitive conclusions have been checked against live official store documentation during the current run, not only against bundled local notes
- every sensitive permission maps to a user-facing feature with a clear necessity statement
- every permission description reflects the real platform declaration, trigger point, and denial fallback
- common high-risk permissions that are not declared are explicitly identified as absent when that helps prevent stale or copied review text
- the app requests the minimum permission scope and has a less-invasive fallback when policy expects one
- if login gates any content, or if an important review path is gated, the final ASO document includes a reusable test account and step-by-step access instructions for Google Play reviewers
- if Firebase Authentication backs the gated path, the reviewer account has been created or refreshed in Firebase and the credentials have been verified by an actual sign-in attempt before they are written into the ASO document
- if no login is required for the reviewed build, the final ASO document still states that explicitly and gives the reviewer a no-account path through the app
- screenshots and previews show the real app experience
- pricing, IAP, ads, and subscriptions are not hidden or misrepresented
- competitor names, trademarks, rankings, and irrelevant phrases are not used to game search
- `What's New` or release notes are specific when the change is material

If any claim cannot be verified, remove it or mark it as blocked.
If a reviewer account cannot be created or login cannot be validated, do not present reviewer access as complete.
If live official policy docs cannot be checked, mark policy verification as blocked or partial rather than silently treating the bundled summary as authoritative.

### 6. Deliverables

Default deliverables:

1. one final ASO document that includes competitor evidence, keyword inventory, metadata recommendations, permission-to-feature mapping, explicit absent-permission notes where useful, Google Play reviewer access details, login test access details when applicable, policy-verification notes, and compliance risks
2. one to three copy variants per store if rewriting is requested

For Google Play-focused work, the final ASO document should normally include:

- a `Sensitive Permissions And Feature Mapping` section
- a `Google Play Review Access` section
- either validated reviewer credentials or an explicit statement that no reviewer account is required for the reviewed build

## Do Not

- do not treat category-top apps as automatic direct competitors
- do not write one blended description for both stores
- do not invent keyword volume, rank, or growth numbers
- do not claim privacy, offline processing, or AI capabilities that are not clearly supported
- do not add trademarked terms, competitor names, or promotional pricing language to metadata just to capture traffic
- do not create a separate permissions markdown file; keep permission analysis inside the final ASO document
- do not omit test credentials or reviewer steps when login, membership, region lock, or any other access gate exists
- do not rely on a stale spreadsheet, old release note, or guessed credentials for Google Play review access
- do not treat "we have Firebase Auth in the app" as enough; if reviewer access is needed, ensure the Firebase reviewer account really exists and can sign in
- do not leave placeholder reviewer credentials in a document that is being presented as submission-ready unless the blocker is called out explicitly
- do not rely on `references/policies.md` alone for final policy claims when network access is available
- do not present a task as policy-verified if official Apple / Google pages were not checked during the current run
