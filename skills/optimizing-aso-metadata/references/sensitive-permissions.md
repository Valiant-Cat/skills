# Sensitive Permissions Mapping

Checked on 2026-03-24.

Use this file when the ASO task touches privacy claims, permissions, data safety, or protected resources.

The goal is not just to list permissions. The goal is to prove:

1. which feature uses the permission
2. why the feature cannot work without that scope
3. whether a narrower alternative exists
4. what the app does if the user declines

## Core rule

If a permission does not map to a clear user-facing feature, treat it as a policy and ASO risk.

## Photo-management project mapping

This skill was seeded by a photo-management / photo-cleanup project. For that project shape, use this default table.

| Permission | Platform examples | Feature in this project | Why it may be needed | Default decision |
| --- | --- | --- | --- | --- |
| Photo/media read access | iOS: `NSPhotoLibraryUsageDescription`  Android: `READ_MEDIA_IMAGES`, `READ_MEDIA_VIDEO` | scan camera roll, detect duplicates, cluster similar photos, search or organize by month | the app must inspect the user's selected or library media to identify what to clean or organize | allowed if library-wide cleanup is core |
| Photo-library add or media write access | iOS: `NSPhotoLibraryAddUsageDescription` or photo-library write flows  Android: MediaStore write/delete flows | save organized output, save compressed copies, remove duplicates after user confirmation | the app must persist user-requested changes back to the library or device storage | allowed only for user-driven save/delete actions |
| All files access | Android: `MANAGE_EXTERNAL_STORAGE` | no baseline core feature in this project requires it | photo cleanup and organization usually work with granular media access or a picker | default: do not request |
| Camera | iOS: `NSCameraUsageDescription`  Android: `CAMERA` | none in the baseline project | organizing or cleaning existing photos does not require live capture | default: do not request |
| Microphone | iOS: `NSMicrophoneUsageDescription`  Android: `RECORD_AUDIO` | none in the baseline project | photo cleanup does not require audio capture | default: do not request |
| Contacts | iOS: `NSContactsUsageDescription`  Android: `READ_CONTACTS` | none in the baseline project | the cleaning flow is not contact-dependent | default: do not request |
| Foreground location | iOS: `NSLocationWhenInUseUsageDescription`  Android: `ACCESS_COARSE_LOCATION`, `ACCESS_FINE_LOCATION` | usually none in the baseline project | browsing photo locations can often rely on EXIF or library metadata instead of live device location | default: do not request |
| Background location | iOS: `NSLocationAlwaysAndWhenInUseUsageDescription`  Android: `ACCESS_BACKGROUND_LOCATION` | none | no photo-cleaning core use case justifies continuous background access | do not request |
| Face ID / biometric unlock | iOS: `NSFaceIDUsageDescription`  Android: biometric flows | only if the app has a private vault or locked album | needed to unlock hidden albums or private storage without a passcode | request only when private vault is a shipped feature |

## How to write the permission note

Each sensitive permission should have a one-line product mapping in the working memo:

```text
Permission: Photo library read
Feature: Duplicate-photo scan and timeline organization
Why needed: The app must inspect the user's existing media set to identify duplicates and group photos.
Fallback if denied: Manual import or limited-library selection only.
```

## Platform-specific policy reminders

### Apple

- Usage strings must clearly explain why the app needs the protected data or resource.
- App Review checks whether the purpose string and the real feature match.
- App Privacy details in App Store Connect must match real collection and transmission behavior.

Useful official sources:

- <https://developer.apple.com/app-store/app-privacy-details/>
- <https://developer.apple.com/documentation/bundleresources/information-property-list/nslocationalwaysandwheninuseusagedescription>
- <https://developer.apple.com/documentation/BundleResources/Information-Property-List/NSContactsUsageDescription>
- <https://developer.apple.com/documentation/PhotoKit/delivering-an-enhanced-privacy-experience-in-your-photos-app>

### Google Play

- Use the minimum permission scope necessary.
- Respect denial and provide fallback where reasonable.
- Photo and video access must be directly related to app functionality; one-time or infrequent access should prefer a system picker.
- Special or restricted permissions such as all-files access require stronger justification and may require review.
- Location cannot be requested only for ads or analytics.

Useful official sources:

- <https://developer.android.com/training/permissions/requesting-special>
- <https://developer.android.com/about/versions/13/behavior-changes-13>
- <https://developer.android.com/training/permissions/requesting>
- <https://support.google.com/googleplay/android-developer/answer/16543315?hl=en>
- <https://support.google.com/googleplay/android-developer/answer/9888170>

## Review checklist

Before approving ASO copy, answer all of these:

- Which exact feature uses each sensitive permission?
- Is that feature already shipped?
- Is there a narrower permission or system picker alternative?
- What still works if the user denies the permission?
- Does the store copy over-promise privacy or security beyond what the app and policy declarations support?
