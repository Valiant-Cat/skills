# ASO Data Requirements

Use this file when you need to define the minimum research packet for an ASO task.

## Required product inputs

- app name
- platform: `ios`, `android`, or both
- package ID / bundle ID / app ID
- primary countries and locales
- core feature list
- current metadata
- current screenshots / preview assets
- pricing, subscriptions, ads, and trial structure
- permissions and privacy policy

If available, also collect:

- existing install CVR
- search term coverage or rank exports
- top traffic countries
- prior ASO tests and rejected copy

## Competitor set design

Always split competitors into three groups.

### Direct competitors

Same job-to-be-done and likely same search language.

### Category leaders

Top apps in the store category. Useful for:

- market expectations
- asset quality bar
- monetization context

Not always useful for direct copy imitation.

### Adjacent substitutes

Apps that steal similar search traffic or solve the problem indirectly.

## Minimum Sensor Tower export pack

For each important competitor, prefer:

1. `metadata`
2. `sales`
3. `keywords`

Add these when needed:

4. `keyword-research`
5. `top-apps`
6. `rankings`
7. `reviews`
8. `review-summary`
9. `ratings`

## Suggested workspace structure

```text
research/
  sensortower/
    search-*.json
    *-metadata.json
    *-sales.json
    *-keywords.json
    kw-*.json
    reviews-*.json
reports/
  aso-research.md
  keyword-inventory.csv
  store-copy-ios.md
  store-copy-android.md
  compliance-checklist.md
```

## Questions that the data should answer

- Which terms already drive discovery?
- Which valuable terms are uncovered or weakly ranked?
- Which competitors dominate direct intent?
- Which claims appear repeatedly across the category?
- Which messages convert category browsers into installers?
- Which claims are unsafe because the app, privacy policy, or permissions do not support them?
