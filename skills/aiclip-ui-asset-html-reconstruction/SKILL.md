---
name: aiclip-ui-asset-html-reconstruction
description: "Use when converting AI-generated UI design images/screenshots into reusable transparent PNG assets and a pixel-aligned HTML reconstruction. Extracts AiClip two-step flow: detect/slice visual UI assets, export transparent PNGs, then rebuild HTML using absolute geometry so the result matches the design reference. Also applies Impeccable design quality gates when generating, selecting, or elevating source UI images so the reconstruction preserves stronger hierarchy, UX, typography, color, lighting, and visual taste."
license: CC-BY-NC-4.0-derived-from-AiClip
metadata:
  hermes:
    tags: [ui-reconstruction, assets, imagegen, gpt-image-2, html, png, aiclip, impeccable, design-quality]
    source_repo: https://github.com/shouzi23333-rgb/AiClip
    related_skills: [codex, codex-project-workflows, popular-web-designs, impeccable]
---

# AiClip UI Asset → HTML Reconstruction

## Overview

This skill packages the core AiClip workflow into an agent-friendly runbook for taking a UI design image from CodeX ImageGen, GPT Image 2, or another image generator and turning it into:

1. transparent-background PNG assets for non-text visual elements, and
2. a reconstructed HTML page that aligns with the original design image.

It is derived from AiClip (`shouzi23333-rgb/AiClip`, CC-BY-NC-4.0). Preserve attribution and do not use this derived workflow for commercial reuse unless the license allows it.

The key principle is **do not ask the coding agent to redraw everything**. Use the source image as the visual reference, extract opaque/transparent assets, then position those assets in HTML at the exact source coordinates while coding simple text, cards, backgrounds, and layout containers.

The quality principle is **do not preserve weak generated design blindly when the user asked for a better one**. Use Impeccable's design standards to shape or select the source UI before slicing, and to polish the coded reconstruction after assembly. Fidelity and taste are separate controls:

- `exact`: match the source image as closely as possible, even if the source is visually mediocre.
- `elevated`: keep the source layout and product intent, but improve hierarchy, spacing, typography, color, light, affordances, and UX clarity before or during reconstruction.
- `variant`: produce a second, better design variant while keeping the original pixel reconstruction available for comparison.

## When to Use

Use this skill when the user asks to:

- convert an AI-generated UI screenshot/design into HTML/CSS;
- export all UI visual elements as transparent PNGs;
- rebuild a design with high visual fidelity rather than approximate icon libraries;
- use CodeX ImageGen / GPT Image 2 outputs as implementation input;
- preserve exact icons, illustrations, logos, avatars, product images, decorations, gradients, and ornamental visuals.
- improve or regenerate an AI UI reference before slicing so the final HTML feels more polished, premium, usable, or on-brand.

Do **not** use this for pure hand-coded UI with no screenshot/reference image, or for production web apps where semantic/responsive HTML matters more than screenshot-perfect visual reconstruction.

## Inputs and Outputs

Minimum inputs:

- `source.png` or `source.jpg`: original UI design/reference image.
- Target page size, usually the image's pixel size. If responsive output is required, preserve this as the design coordinate system and scale the wrapper.

Optional inputs:

- Manual asset manifest with bounding boxes if the model or agent already knows them.
- Existing extracted assets from another tool.

Expected output package:

```text
ui-reconstruction/
  source.png
  assets/
    asset_001_search.png
    asset_002_logo.png
    ...
  assets.json
  index.html
  prompt.md
```

`assets.json` should keep geometry so future agents can reuse the package:

```json
{
  "version": "generated-assets-1.0",
  "source": "source.png",
  "sourceSize": { "width": 390, "height": 844 },
  "assets": [
    {
      "id": "asset_001",
      "file": "assets/asset_001_search.png",
      "type": "icon",
      "sourceBBox": [320, 48, 24, 24],
      "htmlBBox": [320, 48, 24, 24],
      "prompt": "search icon from top bar",
      "pipeline": "ai-chroma"
    }
  ]
}
```

Coordinate format is always `[x, y, width, height]` in original source pixels.

## Core Flow

### Step 0 — Impeccable design quality gate

Run this gate before slicing if the user asks for better design quality, if the source is AI-generated, or if the screenshot shows obvious AI design tells.

1. **Choose reconstruction intent.**
   - `exact`: user wants pixel fidelity. Do not redesign. Use Impeccable only to avoid implementation mistakes such as flat typography, incorrect shadows, poor contrast, or broken hierarchy in coded text/CSS.
   - `elevated`: user wants the same UI made better. Preserve the product concept and rough geometry, but improve weak visual decisions before final HTML.
   - `variant`: user wants a new refined version. Keep the original reconstruction and create a separate improved source/HTML pair.

2. **Load design context when available.**
   - Check for `PRODUCT.md` and `DESIGN.md` in the project root, current directory, parent directories, and relevant feature folders.
   - If an Impeccable skill is installed, use its setup discipline: determine `brand` vs `product` register, load the matching guidance, and apply the shared design laws.
   - If no design context exists, infer a narrow scene: who uses this UI, where, under what light, for what job, and with what emotional tone. Use that scene to choose theme, palette, density, and motion.

3. **Reject common AI UI tells before asset extraction.**
   - Do not carry forward gradient text, decorative glassmorphism, nested cards, identical icon-card grids, side-stripe borders, generic purple/blue SaaS gradients, weak gray-on-color contrast, or hero-metric filler.
   - Avoid pure `#000` and `#fff`; use subtly tinted neutrals and deliberate OKLCH-like color roles when coding CSS.
   - Prefer real hierarchy: meaningful scale steps, purposeful spacing rhythm, clear affordances, readable labels, and lighting/shadows that explain depth.

4. **For generated or regenerated source images, write a design-grade prompt.**
   Include:
   - product/register and scene;
   - target device and exact canvas size;
   - information hierarchy and primary user action;
   - palette strategy, material/light direction, typography feel, spacing density, and accessibility constraints;
   - instruction that normal UI text should remain clean and readable, while logos or ornamental marks may be image assets.

Do not let this gate break the AiClip contract. If the task is `exact`, the source image remains the source of truth. If the task is `elevated` or `variant`, record the design changes in `prompt.md` and keep geometry changes intentional.

### Step 1 — Picture processing: split image into transparent PNG assets

1. **Analyze the design image and create a manifest.**
   - Identify visual assets: icons, illustrations, decorations, logos, avatars, product images, banners, custom backgrounds.
   - Do not export normal text as PNG unless it is part of a logo/image or exact typography cannot be coded.
   - Separate `semantic` UI from raster assets: cards, forms, buttons, charts, tab bars, text, shadows, and simple backgrounds should usually be HTML/CSS unless exact source pixels are required.
   - Use `asset` / `regenerate` / `crop` style strategy tags:
     - `ai-chroma`: icons, illustrations, custom decorations, uncertain assets that need background cleanup.
     - `crop`: photos, product images, avatars, logos, banners, screenshots, anything whose original pixels should be preserved.

2. **Create an asset sheet.**
   - Crop each asset bbox from the source image.
   - Place crops into a padded transparent sprite sheet.
   - Record for each asset: `id`, `sourceBBox`, `sheetBBox`, `cropSearchBBox`, `assetPipeline`, `assetName`, `type`, and `prompt`.

3. **For `ai-chroma` assets, ask GPT Image 2 / ImageGen to produce a green-screen asset sheet.**
   Use the prompt pattern from `references/aiclip-core-flow.md`: same canvas size; same asset count and positions; preserve all foreground shape/color/detail; paint every non-asset pixel exactly `#00ff00`; no transparency, labels, borders, extra assets, or watermarks.

4. **Post-process the green-screen output into transparent PNGs.**
   - Use the bundled `scripts/process_chroma_icons.py` or an equivalent Python/Pillow workflow.
   - For green screen: remove `#00ff00`, feather anti-aliased edges, despill green edges, trim transparent bounds with small padding.
   - For direct crop assets: crop source pixels and, only for small icons on simple backgrounds, remove edge-sampled neutral background.

5. **Validate asset quality.**
   - Reject empty/too-sparse outputs.
   - Flag likely black blocks, wrong backgrounds, or missing alpha.
   - Compare each PNG's aspect ratio and visible area against the source bbox.

### Step 2 — Page assembly: reconstruct the HTML page

1. **Use the original source image as the coordinate system.**
   - Create a root `.stage` with fixed `width` and `height` equal to the design image.
   - For phone/webview previews, wrap it in a scalable container.

```css
.viewport { width: 100vw; min-height: 100vh; display: grid; place-items: center; background: #000; }
.stage { position: relative; width: 390px; height: 844px; overflow: hidden; transform-origin: top center; }
@media (max-width: 390px) { .stage { transform: scale(calc(100vw / 390)); } }
```

2. **Place every extracted asset at its source bbox.**

```html
<img class="asset" src="assets/asset_001_search.png" style="left:320px;top:48px;width:24px;height:24px" alt="" />
```

```css
.asset { position: absolute; object-fit: contain; display: block; pointer-events: none; }
```

3. **Code structural UI as HTML/CSS, not images.**
   - Use divs for cards, panels, tab bars, chips, buttons, backgrounds, borders, shadows.
   - Use text nodes for readable labels; match font size, weight, line-height, letter spacing, color, and alignment.
   - If generated text is illegible, use visually similar placeholder text and preserve layout.
   - In `elevated` mode, improve coded typography, contrast, spacing, depth, and state clarity while keeping the same layout skeleton.
   - Avoid visual shortcuts Impeccable bans: gradient text, decorative glass cards, nested cards, colored side-stripe borders, and monotonous repeated card grids.

4. **Layer order matters.**
   - Background gradients/cards first.
   - Large photos/illustrations next.
   - Text and controls above.
   - Icons/decorations last if they overlay controls.

5. **Avoid library substitutions.**
   - Do not replace packaged icons with FontAwesome, Lucide, SF Symbols, Material Icons, or SVG approximations unless the asset is missing.
   - Do not redraw logos/illustrations in CSS if a packaged PNG exists.

### Step 3 — Impeccable polish and validation

After the first HTML pass renders:

1. **Run visual fidelity validation.**
   - Screenshot `index.html` at the source dimensions.
   - Compare against `source.png`; fix geometry, layer order, clipping, asset scale, typography, shadows, colors, and radii.

2. **Run design-quality validation.**
   - For `exact`, check that coded elements do not degrade the source. Do not improve beyond the reference unless it fixes readability, accessibility, or implementation artifacts.
   - For `elevated` or `variant`, apply Impeccable-style polish: sharper hierarchy, stronger light/material logic, fewer generic AI motifs, better contrast, more intentional spacing, and clearer primary action.

3. **Document the mode and tradeoffs.**
   - `prompt.md` should say whether the output is `exact`, `elevated`, or `variant`.
   - If the HTML intentionally differs from `source.png`, list the differences and why they improve UX or visual quality.

## Codex / CodeX Usage Pattern

When handing this to Codex or another coding agent, provide the package and say:

```md
Use the aiclip-ui-asset-html-reconstruction skill.
Input: `source.png` plus `assets/` and `assets.json`.
Build `index.html` that matches `source.png` pixel-for-pixel at the source coordinate size.
Use all packaged PNG files directly; do not replace them with icon libraries or redraws.
Position assets using `sourceBBox` / `htmlBBox`. Code text, cards, backgrounds, shadows, and simple shapes in HTML/CSS.
If the task asks for a more premium, beautiful, polished, or user-friendly result, apply Impeccable design quality gates and mark the output as `elevated` or `variant`; otherwise keep `exact` fidelity.
After implementation, render/screenshot the HTML at the source image dimensions and compare visually against `source.png`; iterate until alignment is as close as possible.
```

## Recommended Commands

Install dependencies for the chroma processor if needed:

```bash
python3 -m pip install Pillow
```

Run the chroma processor against a generated green-screen sheet:

```bash
python3 scripts/process_chroma_icons.py \
  --input generated-sheet.png \
  --out-dir assets \
  --manifest asset-sheet-manifest.json \
  --key green \
  --padding 0.08 \
  --tolerance 92 \
  --softness 42 \
  --spill-threshold 24 \
  --edge-background-tolerance 28 \
  --neutral-tolerance 28 \
  --isolated-light-luma 245 \
  --icon-halo-luma 240 \
  --icon-halo-chroma 18
```

If you have a simple uniform grid instead of a manifest:

```bash
python3 scripts/process_chroma_icons.py \
  --input generated-sheet.png \
  --out-dir assets \
  --grid 3x2 \
  --names search,cart,home,profile,logo,badge \
  --key green
```

## Reconstruction Acceptance Checklist

Before declaring success:

- `assets/` contains transparent PNGs with valid alpha channels.
- `assets.json` includes source image size and per-asset source/html bboxes.
- `index.html` renders at the same base dimensions as `source.png`.
- All packaged assets are used in the page or explicitly marked unused with a reason.
- No icon library substitutions for extracted assets.
- Screenshot of HTML at source dimensions visually aligns with `source.png`: key edges within ~1-3 px; same hierarchy, spacing, colors, typography, shadows, radius; important mobile/WebView content not clipped; no gutters or half-width backgrounds for full-bleed designs.
- Reconstruction mode is recorded as `exact`, `elevated`, or `variant`.
- Impeccable quality gate has been applied when the task asks for better design: no obvious AI UI tells, readable typography, deliberate spacing rhythm, accessible contrast, coherent lighting/depth, clear primary action.
- Any intentional design improvements are documented in `prompt.md` rather than silently drifting from the source.

## Common Pitfalls

- **Model moves assets on the sheet:** batch assets by similar size/type and ask for exact same canvas and positions.
- **Green halo remains:** increase despill/softness slightly; keep key color exact `#00ff00` in prompt.
- **White card behind icon is preserved:** clarify that square/card backgrounds are not part of the asset.
- **Asset is trimmed too tightly:** add transparent padding or preserve `htmlBBox` with `object-fit: contain`.
- **HTML looks close but not exact:** switch to absolute layout inside a fixed-size stage first; add responsive scaling only after matching the base screenshot.
- **Text exported as images:** avoid unless absolutely necessary; coded text is easier to align and localize.
- **Polish breaks fidelity:** choose `exact` or create a separate `variant`; do not silently redesign a source image the user asked to preserve.
- **Beautiful source becomes flat HTML:** use Impeccable polish on coded CSS, especially typography, contrast, depth, lighting direction, spacing rhythm, and primary-action clarity.

## References

- `references/aiclip-core-flow.md` — extracted architecture, prompts, schemas, and implementation notes from AiClip.
- `templates/reconstruction-prompt.md` — handoff prompt for Codex/CodeX/GPT coding agents.
- `templates/asset-manifest.schema.json` — expected asset manifest shape.
- `scripts/process_chroma_icons.py` — AiClip-derived green-screen-to-transparent PNG processor.
