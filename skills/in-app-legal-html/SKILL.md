---
name: in-app-legal-html
description: Use when a mobile app needs Privacy Policy and Terms of Service content drafted from actual app behavior, styled as static HTML, and wired into an in-app legal viewer or settings/about entry. Trigger for Google Play or App Store readiness work, user-data disclosure pages, WebView or WKWebView legal pages, or app-embedded legal content on Android or iOS.
---

# In-App Legal HTML

## Overview

Prepare app-embedded Privacy Policy and Terms of Service pages that match the product's real behavior, render cleanly on mobile, and are easy to open from the app. Do not invent data practices, permissions, retention rules, or compliance claims.

This skill is for product-ready in-app legal content. It is not a substitute for legal counsel or for distribution-channel requirements such as a public privacy-policy URL in Google Play or App Store Connect disclosures.

When the user or project provides a canonical developer name or support email, treat those values as mandatory source-of-truth inputs and propagate them consistently across app code, public legal pages, and store metadata. Do not silently substitute a repo owner name, GitHub issue tracker, or generic contact channel.

## Workflow

1. Inspect the app before drafting.
   Read permissions, onboarding, settings, auth, sync, notifications, analytics, camera/file flows, and backend integrations.
   Build a factual list of:
   - account data
   - financial or user content
   - optional sensitive inputs such as SMS, camera, gallery, PDF, contacts, location
   - third-party processors such as Firebase, Google Analytics, push providers
   - whether the app supports account creation, password reset, or account deletion

2. Write policy content from observed behavior only.
   For Privacy Policy, cover:
   - who the app is and how to contact the developer
   - what data is collected or processed
   - why the data is used
   - when data is shared and with whom
   - permissions and user choices
   - retention and deletion handling
   - security, children, international processing, policy updates

   For Terms of Service, cover:
   - eligibility and account responsibility
   - license and allowed use
   - what the app does and what it does not do
   - user responsibility for submitted or confirmed data
   - availability, service changes, disclaimers, termination, contact

3. Keep policy language aligned with reality.
   Do not claim:
   - data is never shared if third-party processors are used
   - data is encrypted end-to-end unless verified
   - data is deleted on demand unless a real deletion flow exists
   - legal/financial advice disclaimers that contradict the product

4. Call out platform-policy gaps explicitly.
   If relevant, note remaining obligations such as:
   - Google Play requires a publicly accessible privacy-policy URL; in-app HTML alone is insufficient
   - if the app allows account creation, Google Play may require account-deletion support and corresponding Data safety disclosures
   - App Store submissions may require a privacy policy URL in App Store Connect and accurate App Privacy nutrition-label disclosures
   - if the app supports account creation, Apple requires account deletion initiation from within the app
   - sensitive permissions such as SMS must be justified by core functionality and reflected accurately in policy text
   - do not describe the app as store-policy-compliant if account creation exists but there is no real user-facing account deletion initiation path

5. Resolve public URL uniqueness before deployment.
   If Firebase Hosting or another public host is shared across multiple apps:
   - prefer a dedicated hosting site for this app's legal pages
   - if a dedicated site is unavailable, use app-specific public paths rather than shared roots such as `/privacy` or `/terms`
   - update every source of truth together: hosting config, app constants, in-app entry points, ASO/store metadata, and any backend/express routes that expose the legal pages
   - verify the chosen URL does not collide with another app's legal surface
   - do not deploy a shared-root legal route for one app if it can override another app's public policy URLs

6. Implement mobile-friendly static HTML.
   Prefer:
   - one HTML file per document
   - responsive layout
   - readable typography
   - anchored table of contents for long documents
   - high contrast in light and dark environments
   - polished but restrained styling; legal pages should feel trustworthy, not flashy

7. Wire the pages into the app.
   On Android, the default pattern is:
   - store files under `app/src/main/assets/legal/`
   - create a legal document type/router model
   - load the HTML with a safe `WebView` or equivalent viewer
   - expose entry points from settings/about/account screens

   On iOS, the default pattern is:
   - store files in the app bundle, for example under `Resources/Legal/`
   - create a small legal document enum or router
   - load the HTML in `WKWebView` or a native wrapper
   - expose entry points from Settings, About, Profile, or onboarding/account surfaces

8. Verify before claiming completion.
   At minimum verify:
   - document route/asset mapping
   - build passes
   - the app can open both documents
   - text is readable on device
   - the public privacy-policy URL and terms URL return the expected content with HTTP 200
   - the app uses the same deployed URLs that store metadata uses; no stale domain or stale path remains

## Android Pattern

For Android apps, use this structure unless the project already has a different legal-content system:

- `app/src/main/assets/legal/privacy-policy.html`
- `app/src/main/assets/legal/terms-of-service.html`
- a small Kotlin model such as `LegalDocumentType`
- a dedicated screen that loads HTML from assets
- settings/about items that navigate to each legal page

Recommended `WebView` posture:

- disable JavaScript unless required
- disable file/content access unless required
- use local asset loading only
- avoid unnecessary reloads on recomposition

## iOS Pattern

For iOS apps, use this structure unless the project already has a different legal-content system:

- bundled HTML files such as `Resources/Legal/privacy-policy.html`
- bundled HTML files such as `Resources/Legal/terms-of-service.html`
- a small Swift enum such as `LegalDocumentType`
- a `WKWebView`-based viewer or a SwiftUI/UIKit wrapper
- settings/about items that navigate to each legal page

Recommended `WKWebView` posture:

- load bundled files rather than remote URLs for in-app viewing
- keep JavaScript disabled unless the content truly requires it
- avoid hidden tracking or remote script injection in legal pages
- keep typography and spacing tuned for long-form reading on iPhone

## Content Guardrails

- Refer to the app or developer name used in distribution.
- Include a real contact email.
- Match the app's actual sensitive-permission behavior.
- Match the app's actual App Privacy / Data safety disclosures.
- If the app supports account creation, cover password reset, account deletion handling, retention, and local-vs-remote data boundaries explicitly.
- Distinguish local on-device data from remote account or backend data. Do not blur them together.
- If the app is localized, start from a single accurate source version before translating.
- Prefer direct, specific prose over generic legal boilerplate.

## Common Mistakes

- Writing generic policy text before inspecting code and permissions
- Treating optional permissions as always-on collection
- Hiding important disclosures behind vague phrases like "may collect data as needed"
- Forgetting Firebase Analytics, FCM tokens, or cloud storage processors
- Using shared hosting roots like `/privacy` or `/terms` for one app inside a multi-app Firebase project
- Updating HTML and forgetting to update the deployed public URL in app constants or store metadata
- Claiming store compliance while account deletion, App Privacy disclosures, or public policy URLs are still missing

## Done Criteria

This skill is complete when:

- Privacy Policy and Terms are grounded in observed app behavior
- both documents render well as static in-app HTML
- both documents are reachable from the app UI
- public legal URLs are unique for the app and do not override another app's legal URLs in a shared hosting environment
- developer name and support email match the canonical values provided by the user or project
- verification has been run
- any remaining Google Play or App Store policy gaps are explicitly reported
