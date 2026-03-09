---
name: mobile-app-competitive-research
description: Deep-research a mobile app competitor from a Google Play or App Store URL, package/bundle ID, or app name. Use when the user wants a full competitor analysis, Sensor Tower-backed market sizing and ad/ASO/review insights, hidden features and liked features mined from user reviews, creative asset links included in the report, and follow-on product and technical documents for building an AI-enhanced product that can beat the competitor, then save locally and commit/push to GitHub.
---

# Mobile App Competitive Research

Use this skill when the user wants a serious mobile-app competitor teardown, not a lightweight summary.

This skill produces up to three deliverables:
1. A competitor research document
2. A product document for an AI-enhanced product that can outperform the competitor
3. A technical development document / tech spec

If the target is a mobile app and Sensor Tower data is relevant, you must also use [sensortower-research](../sensortower-research/SKILL.md).

## Inputs To Resolve First

Resolve the target app from one of:
- Google Play URL
- App Store URL
- Android package ID
- iOS bundle ID / app ID
- App name plus store

Also resolve:
- output workspace and existing doc conventions
- whether the repo should store raw exports
- whether the user wants commit/push; if not stated and the task is clearly repository-backed, default to saving locally first and only push when requested

## Default Output Locations

If the repo already has a clear convention, follow it. Otherwise use:
- competitor report: `reports/YYYY-MM-DD-<slug>-competitive-research.md`
- product doc: `researches/products/YYYY-MM-DD-<slug>-ai-product-doc.md`
- tech doc: `researches/products/YYYY-MM-DD-<slug>-tech-spec.md`
- Sensor Tower raw exports: `researches/<slug>/sensortower/`

Use a stable slug derived from the app name or package ID.

Read [references/output-templates.md](references/output-templates.md) when drafting deliverables.

## Workflow

### 1. Build The Evidence Base

Start with public store information:
- title, subtitle, description, screenshots, permissions, update date, install range, rating
- obvious feature set and positioning

Then use [sensortower-research](../sensortower-research/SKILL.md) for:
- metadata
- sales / downloads / revenue
- top-apps and category position
- ratings and reviews
- review-summary and review-insights
- keywords and keyword-research
- creatives and, when needed, raw creative endpoints

Export raw files before summarizing. Do not write a report from memory or from terminal output alone.

### 2. Mine Reviews For Both Pain And Love

Do not stop at complaint clustering. Reviews must be mined for:
- main pain points
- hidden features or hidden product behaviors
- user-loved features
- user-loved content types and use cases
- expectation mismatches
- monetization complaints
- localization complaints
- feature requests

Important:
- some features are only visible in reviews, not on the store page
- some of the most valuable insights are about why users keep using the app, not why they churn
- read representative samples from the biggest positive and negative clusters before concluding

Always extract:
- what users hate
- what users love
- what users think the app is “for”
- what users compare it against
- what changed after updates

### 3. Analyze Marketing And UA

Use Sensor Tower ad/creative data plus store context to analyze:
- buy-side network coverage
- paid vs organic acquisition balance
- main ad angles
- likely audience targeting
- format mix: static, video, feed, reels, stories, interstitial, etc.
- creative style: UGC, demo, before/after, spokesperson, claims-heavy, feature-heavy

The report must include direct creative links when available:
- video preview URL
- video asset URL
- static asset URL
- thumbnail URL

If local copies are saved, include the local folder path too.

Do not just say “creatives focus on convenience.” Explain what the visuals, copy, people, scenes, and UI framing are doing.

### 4. Write The Competitor Report

The competitor report must be comprehensive, evidence-backed, and opinionated. Cover:
- product positioning
- feature inventory
- core feature priorities
- hidden features and hidden behaviors from reviews
- user-loved features and why users like using the app
- monetization model
- ad tolerance and monetization risk
- UA strategy
- main creative directions
- ASO strategy
- user scale
- geography
- user demographics / likely personas
- core technology and engineering implications
- core advantages
- core weaknesses
- policy / compliance / trust risks
- what matters most if someone wants to beat this product

When data conflicts across sources, say so explicitly and state which source you trust for that claim.

### 5. Turn Research Into A Better Product Plan

After the competitor report, write a product document for the AI-enhanced product the user wants to build.

This document must not be generic. Base it on:
- the competitor’s strongest retained use cases
- the competitor’s most hated pain points
- the competitor’s overpromises
- the unmet requests in reviews
- the places where AI can create actual workflow advantage instead of surface decoration

Push beyond “add AI recommendations.” Define:
- target user and wedge
- user jobs-to-be-done
- product strategy
- core AI features
- non-AI core table stakes
- differentiation vs competitor
- user flows
- monetization strategy
- rollout priorities
- success metrics

The goal is to explain how to beat the competitor, not how to clone it.

### 6. Write The Technical Development Document

Translate the product doc into a technical plan. Cover:
- system architecture
- app modules
- AI subsystem responsibilities
- model/runtime decisions
- data flow
- storage and sync
- content ingestion / playback / indexing layers when relevant
- privacy and compliance
- observability
- experimentation
- release plan
- implementation phases
- major technical risks and mitigations

Be concrete about what must be built first and what can wait.

### 7. Save, Commit, Push

Save all requested deliverables locally.

If the user asks for GitHub submission:
- stage only the intended docs and raw evidence files
- do not commit secrets, auth tokens, or stray OS files like `.DS_Store`
- use a clear non-interactive commit message
- push to the current remote/branch unless the user specifies otherwise

## Quality Bar

The work is not done if any of these are missing:
- Sensor Tower-backed scale, geography, ASO, review, and creative evidence when relevant
- explicit extraction of hidden features from reviews
- explicit extraction of user-loved features / why users like using the app
- direct creative links in the report when available
- a product doc that explains how to beat the competitor with AI
- a technical doc that is detailed enough to guide implementation
- local saved files
- Git commit/push when requested

## Evidence Rules

- Prefer exact windows and country scopes for claims
- Separate evidence from inference
- Do not invent missing data
- If a creative endpoint yields sparse results, say it is a limited sample instead of pretending the coverage is exhaustive
- If a review pattern appears market-specific, say which market showed it

## Deliverable Style

Favor crisp, structured markdown. Keep the analysis high-signal:
- clear sectioning
- concrete numbers
- representative examples
- direct implications

Avoid bland summaries. The output should help a product team make decisions.
