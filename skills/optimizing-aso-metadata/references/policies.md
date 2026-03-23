# Store Policies And Metadata Constraints

Checked on 2026-03-23.

Use this file before writing or approving App Store or Google Play metadata.

## Apple App Store

Primary sources:

- <https://developer.apple.com/app-store/review/guidelines/>
- <https://developer.apple.com/app-store/product-page/>

### Rules that matter most for ASO

- App name can be up to `30` characters.
- Subtitle can be up to `30` characters.
- Promotional text can be up to `170` characters.
- Keywords are limited to `100` characters total.
- Promotional text does not affect search ranking.
- Do not add unnecessary keywords to the description just to improve search results.
- Do not include specific prices in the description.

### Review-guideline guardrails

- `2.3 Accurate Metadata`: metadata, privacy information, screenshots, and previews must accurately reflect the real app experience.
- `2.3.1`: do not market features or services the app does not actually offer.
- `2.3.3`: screenshots should show the app in use.
- `2.3.7`: do not pack metadata with trademarked terms, popular app names, pricing information, or irrelevant phrases to game discovery.
- `2.3.12`: material product changes should be described in `What's New`.

### Practical implications

- Do not promise privacy, offline processing, AI automation, or security levels unless the app actually supports them.
- Do not use competitor names or category labels as keyword bait.
- Make screenshot overlays consistent with the shipped UI and real feature set.
- If IAP or subscriptions matter to the value proposition, do not obscure that in the metadata.

## Google Play

Primary sources:

- <https://support.google.com/googleplay/android-developer/answer/9859152?hl=en>
- <https://support.google.com/googleplay/android-developer/answer/16944162?hl=en>

### Rules that matter most for ASO

- App name has a `30` character limit.
- Short description has an `80` character limit.
- Full description has a `4000` character limit.
- Repetitive or irrelevant keyword use in the app name, description, or promotional description can lead to suspension.

### Policy guardrails

- Metadata must not mislead users about the app's functionality.
- Title, icon, or developer name must not imply store performance, ranking, price, or promotion.
- Data safety declarations must be clear and accurate for every app.
- AI-generated-content features still have to comply with existing Google Play policies.
- Intellectual property rules still apply to keywords, copy, screenshots, and branded comparisons.

### Practical implications

- Do not describe roadmap items as released features.
- Do not overstate privacy or data handling if the app requests broad file, photo, or cloud permissions.
- Do not stuff synonyms into the first lines of the description.
- If the app contains ads, subscriptions, or gated features, keep the commercial model consistent across copy, screenshots, and store settings.

## Safe drafting checklist

Before shipping copy, confirm all of these:

- every major claim is supported by the real product
- privacy and security claims match the privacy policy and store declarations
- screenshots and previews show the real app experience
- pricing and subscription references are current and not misleading
- no competitor names, trademark bait, or ranking bait are used in metadata
