---
name: imagegen-icon-mascot
description: Generate polished, cute, premium 3D app icons and mascot icons with GPT-Image/imagegen. Use when the user asks for app icon design, iOS/Android icon assets, mascot icons, cute 3D icons, icon prompts, clickable/high-conversion icon concepts, or visual style extraction based on rounded-square glossy icon grids.
---

# Imagegen Icon Mascot

## Overview

Create beautiful, clickable app icons and mascot icons in the style of premium 3D mobile icon sets: a single charming central subject, soft clay/plastic material, expressive face, crisp silhouette, rich highlights, and strong shelf visibility. Default to production-ready transparent PNG/WebP assets with real alpha corners; create rounded-square gradient tile previews only as optional App Store or marketing variants.

For exact style DNA extracted from the reference grid, read `references/style-system.md`. The visual anchor is `assets/reference-icon-grid.jpeg`. Use `scripts/validate_alpha_corners.py` from this skill folder to verify transparent PNG/WebP deliverables.

## Workflow

1. Clarify the app category, audience, platform, and whether the output should be a finished bitmap icon, prompt only, concept list, or multiple variants.
2. Convert the product idea into one simple metaphor: one object, mascot, or object-character hybrid. Avoid complex scenes.
3. Pick a dominant emotional hook: friendly, helpful, playful, calm, magical, energetic, trustworthy, or premium.
4. Build an icon spec with these fixed layers:
   - Production canvas: 1:1 transparent PNG/WebP, real alpha background, no black corners, no white corners, no fake checkerboard transparency.
   - Optional preview canvas: rounded-square tile with saturated smooth gradient, subtle vignette, inner glow, and enough contrast behind the subject.
   - Subject: one large central 3D object or mascot occupying about 68-82% of the canvas.
   - Face: tiny glossy black eyes and a simple smile unless the brand requires a more serious tone.
   - Lighting: large soft key light from upper-left, rim light, contact shadow, ambient occlusion.
   - Material: soft toy-like clay, glossy plastic, silicone, enamel, or plush depending on subject.
   - Composition: centered, front-facing or slight 3/4 view, oversized simple silhouette, no tiny details.
5. Generate with `image_gen` when the user wants actual images. For transparent deliverables, follow the `imagegen` chroma-key workflow, remove the keyed background locally, and validate the output alpha before finishing.
6. If App Store preview art is needed, create it as a separate rounded-square gradient tile version after the transparent production file exists.
7. Run the alpha validation script on every transparent production file:
   ```bash
   python3 scripts/validate_alpha_corners.py <icon.png>
   ```
8. Inspect the result for shelf impact: readable at small size, clean silhouette, pleasing face, no accidental text, no messy background, no uncanny anatomy.
9. Iterate with one targeted change at a time: silhouette, palette, emotion, material, lighting, or matte cleanup.

## Prompt Template

Use this template for GPT-Image/imagegen prompts. Keep text concise and visual.

```text
Create a premium 3D mobile app icon/mascot asset for <app/category>.

Subject:
<one central metaphor or mascot>, cute object-character hybrid, expressive but simple, tiny glossy black eyes, small friendly smile, oversized rounded shapes, clear silhouette.

Composition:
1:1 transparent production asset, centered subject, subject fills 70-80% of the canvas, slight 3/4 front view, generous padding, no text, no watermark, no UI mockup. The final PNG/WebP must have true alpha transparency at all four corners, with no black corners, no white corners, and no fake checkerboard background.

Style:
high-end cute 3D icon, soft clay/plastic material, toy-like polish, smooth bevels, subtle subsurface softness, crisp edges, handcrafted details, joyful and clickable.

Lighting:
large soft studio key light from upper left, glossy highlights, subtle rim light, soft contact shadow, ambient occlusion, rich depth.

Background:
For production output, transparent background only. If generating with chroma key for later removal, use a perfectly flat solid key color that does not appear in the subject, with no shadow, gradient, texture, reflection, or lighting variation on the background.

Quality:
app-store-ready, refined, charming, vivid, premium, visually striking at small size.
```

## Concept Patterns

Use one of these patterns to turn an app concept into an icon:

- **Mascot object**: make the product object alive with a face, tiny arms, or posture. Best for utility, productivity, finance, wellness, learning.
- **Animal mascot**: use a rounded animal with one accessory that signals the app category. Best for social, kids, language, fitness, coaching.
- **Friendly tool**: camera, microphone, shield, calendar, suitcase, paint palette, map pin, book, battery, lightbulb, document.
- **Emotional symbol**: heart, moon, cloud, sun, water drop, envelope, bell, treasure chest, rocket.
- **Hybrid metaphor**: combine app category + user benefit, such as a smiling shield for privacy, sleepy moon for meditation, or travel suitcase with sunglasses for trip planning.

## Design Rules

- Prefer one hero subject over multiple small objects.
- Make the silhouette readable before adding decorative details.
- Use saturated color contrast: warm subject on cool background, cool subject on warm background, or complementary accent accessories.
- Add one small category cue only when useful: coin, pencil, cap, headphones, brush, map fold, stars, music note, checkmarks.
- Keep the face minimal: two eyes plus smile usually beats complex expressions.
- Use rounded, inflated, tactile forms; avoid flat vector styling unless explicitly requested.
- Avoid realistic horror, gritty texture, hard metal, busy scenes, typography, tiny UI panels, photorealistic hands, and over-detailed backgrounds.
- Default project deliverables are transparent PNG/WebP production files with real alpha corners.
- Do not accept black-corner, white-corner, or fake checkerboard outputs as transparent.
- For GPT-Image-2/built-in imagegen, use the `imagegen` chroma-key workflow for transparent output, then validate and clean the alpha.
- Create rounded-square gradient tile versions only as separate preview/App Store assets.

## Deliverables

For concept work, provide 6-12 icon ideas with:

- metaphor
- subject
- palette
- emotion
- prompt-ready detail

For generation work, provide:

- final prompt
- variant prompts if requested
- saved transparent PNG/WebP production asset path if the generated bitmap is project-bound
- optional rounded-square gradient tile preview path only when requested or useful for App Store presentation
- alpha validation result for every production PNG/WebP
- short notes on which variant best matches the goal

## Quality Checklist

Before finishing, check:

- It works at 64px and still has a recognizable silhouette.
- The subject is centered and not cropped awkwardly.
- The production file has true alpha transparency in all four corners.
- There are no black corners, white corners, fake checkerboard backgrounds, or leftover chroma-key fringes.
- The icon has a clear visual hook in under one second.
- The palette is vivid but not one-note.
- The face feels charming, not uncanny.
- The surface has premium 3D depth: bevels, highlights, shadows, and ambient occlusion.
- There is no stray text, watermark, extra limbs, malformed accessories, or busy background.
