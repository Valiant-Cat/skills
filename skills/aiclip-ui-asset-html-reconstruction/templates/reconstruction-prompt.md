# UI Reconstruction Prompt

Use `source.png` as the original UI reference image and reconstruct the UI with this asset package.

Requirements:

- Choose a reconstruction mode before coding:
  - `exact`: match `source.png` as closely as possible.
  - `elevated`: preserve the source layout and intent, but improve weak hierarchy, typography, color, lighting, spacing, contrast, and UX clarity.
  - `variant`: keep the original reconstruction and create a separate improved version.
- Recreate the overall layout, hierarchy, spacing, colors, typography, and visual proportions.
- Use the source image dimensions as the base coordinate system.
- Place every provided PNG in `assets/` directly; do not replace packaged icons, logos, illustrations, avatars, product images, or decorations with icon libraries or redrawn SVGs.
- Preserve each asset's transparent background, proportions, colors, and visual details.
- Use `assets.json` `sourceBBox`/`htmlBBox` coordinates for absolute placement.
- Code text, cards, backgrounds, shadows, borders, and simple layout primitives in HTML/CSS.
- Apply Impeccable design quality gates when the mode is `elevated` or `variant`: avoid generic AI UI tells, gradient text, decorative glass cards, nested cards, colored side-stripe borders, weak contrast, flat typography, incoherent shadows, and monotonous repeated card grids.
- In `exact` mode, do not redesign; use design polish only to keep coded text/CSS from degrading the reference.
- Implement a fixed-size `.stage` that can be scaled responsively after the base screenshot matches.
- Render a screenshot at the original source dimensions and compare against `source.png`; iterate until key edges, spacing, and asset positions are within ~1-3 px.
- Record the chosen mode and any intentional visual improvements in `prompt.md`.

Suggested CSS pattern:

```css
.viewport { width: 100vw; min-height: 100vh; display: grid; place-items: center; background: #000; }
.stage { position: relative; overflow: hidden; width: var(--design-width); height: var(--design-height); background: #fff; }
.asset { position: absolute; object-fit: contain; display: block; pointer-events: none; }
```
