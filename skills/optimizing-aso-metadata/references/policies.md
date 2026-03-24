# Store Policies And Metadata Constraints

Checked on 2026-03-24.

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
- If the app touches protected data or resources, its usage strings must explain clearly why that access is needed for a real user-facing feature.

## Google Play

Primary sources:

- <https://support.google.com/googleplay/android-developer/answer/9859152?hl=en>
- <https://support.google.com/googleplay/android-developer/answer/16944162?hl=en>
- <https://support.google.com/googleplay/android-developer/answer/9859455?hl=en>
- <https://support.google.com/googleplay/android-developer/answer/15191715?hl=en>

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
- Restricted and special permissions must be tied to a core user-facing use case, use the minimum scope necessary, and respect user denial.

### Practical implications

- Do not describe roadmap items as released features.
- Do not overstate privacy or data handling if the app requests broad file, photo, or cloud permissions.
- Do not stuff synonyms into the first lines of the description.
- If the app contains ads, subscriptions, or gated features, keep the commercial model consistent across copy, screenshots, and store settings.
- Prefer less-invasive alternatives where the platform expects them, such as photo pickers or narrower media/location scopes.
- Do not request broad photo/video or file access when a one-time picker or granular permission is enough.
- If the app or any part of it is restricted by login, membership, location, or another gate, provide all details needed for reviewer access.
- Reviewer access details should include a stable test account, credentials, and any special login instructions such as OTP, MFA, extra fields, or region requirements.

## Safe drafting checklist

Before shipping copy, confirm all of these:

- every major claim is supported by the real product
- privacy and security claims match the privacy policy and store declarations
- every sensitive permission has a feature-level justification and a user-readable reason
- screenshots and previews show the real app experience
- pricing and subscription references are current and not misleading
- no competitor names, trademark bait, or ranking bait are used in metadata

When documenting permission analysis, include it inside the final ASO document rather than as a standalone permissions memo.
If login exists, also include a `Google Play Review Access` section in the final ASO document with:

- test account identifier
- password or other reusable login secret if applicable
- step-by-step login flow
- OTP/MFA handling notes
- region or device prerequisites
- anything the reviewer must do after login to reach protected content
