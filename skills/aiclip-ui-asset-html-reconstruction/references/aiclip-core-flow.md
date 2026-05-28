# AiClip Core Flow Extraction

Source: https://github.com/shouzi23333-rgb/AiClip
Inspected local clone: /tmp/aiclip_skill_extract
License observed in package.json: CC-BY-NC-4.0

## Relevant Source Files

- `core/manifest.ts`: UI manifest schema, element types, bbox `[x,y,w,h]`, strategies, `assetPipeline` (`crop` or `ai-chroma`).
- `app/api/analyze-image/route.ts`: vision-model analysis, geometry normalization, bbox clamping/refinement, region merging.
- `components/workspace/Workspace.tsx`: asset sheet construction, export package, reconstruction prompt.
- `app/api/generate-assets/planner.ts`: pipeline selection (`crop` vs `ai-chroma`).
- `app/api/generate-assets/route.ts`: GPT Image/image-edit call, green-screen prompt, batching, post-processing orchestration.
- `scripts/process_chroma_icons.py`: green/magenta-screen to transparent PNG extraction.

## Manifest Semantics

UI analysis emits a `UIManifest`:

```ts
type UIManifest = {
  version: '1.0';
  sourceImage: { width: number; height: number; path: string };
  theme: { colors: string[]; fontStyle: string; radius: number[]; shadowStyle?: string };
  elements: Array<{
    id: string;
    type: 'text'|'button'|'card'|'icon'|'image'|'avatar'|'logo'|'illustration'|'background'|'decoration'|...;
    bbox: [number, number, number, number];
    strategy: 'asset'|'code'|'crop'|'regenerate'|'ignore';
    assetPipeline?: 'crop'|'ai-chroma';
    assetName?: string;
    prompt?: string;
    semanticName?: string;
    confidence: number;
    reason: string;
    needsReview: boolean;
  }>;
}
```

Asset sheet generation converts selected elements into an `AssetSheetManifest`:

```ts
type AssetSheetManifest = {
  version: 'asset-sheet-1.0';
  generatedAt: string;
  sourceFileName: string;
  sheetSize: { width: number; height: number };
  assets: Array<{
    id: string;
    sourceBBox: [number, number, number, number];
    sheetBBox: [number, number, number, number];
    cropSearchBBox?: [number, number, number, number];
    exportSize: { width: number; height: number };
    elementType: string;
    strategy: string;
    assetPipeline?: 'crop'|'ai-chroma';
    assetName?: string;
    prompt: string;
    semanticName?: string;
  }>;
}
```

## Asset Sheet Construction Algorithm

1. Filter UI manifest elements with strategy in `asset`, `crop`, `regenerate`.
2. Clamp each source bbox to image bounds.
3. Lay crops into a padded sheet:
   - `padding = 24`
   - `cellGap = 20`
   - `columns = min(3, assetCount)`
   - each column width is `max(asset widths) + padding*2`
   - row height is max asset height in row + padding*2
   - canvas width/height rounded up to multiples of 16.
4. For each asset, draw the source crop into its centered cell.
5. Record `sourceBBox`, `sheetBBox`, and full cell `cropSearchBBox`.

## Pipeline Selection

Use `crop` when preserving original pixels matters:

- product/photo/image/banner/avatar/logo;
- explicit crop strategy;
- small simple decoration whose original background is acceptable or removable.

Use `ai-chroma` when background cleanup or redraw is needed:

- icons, illustrations, complex decorations, uncertain assets;
- regenerate strategy;
- large/complex decorations and backgrounds.

## GPT Image / ImageGen Green-Screen Prompt Pattern

Use this structure for a full sheet:

```text
Use case: background-extraction
Asset type: UI asset sprite sheet for a mobile HTML app
Primary request: Use the provided sprite sheet only as a visual reference. Generate a clean chroma-key version of the same sheet: same canvas size, same asset count, same positions, same scale, with every non-asset pixel painted exact #00ff00.
Style/medium: preserve the original UI asset style exactly; crisp icon/image edges; do not redraw into a different style.
Composition/framing: keep the same canvas size, layout, reading order, asset count, cell/region positions, proportions, scale, and orientation as the input image. Preserve the original empty margins around each asset and around the whole sheet. Do not move, crop, resize, re-center, rearrange, stretch, expand, or add assets.
Color palette: preserve all original foreground colors, text colors, gradients, strokes, shadows, highlights, glows, and details inside each asset.
Scene/backdrop: output a perfectly flat solid #00ff00 chroma-key green background.
Chroma redraw rule: redraw only the asset strokes, filled foreground shapes, text, and real image content. Any enclosed hollow area inside an outline icon may stay #00ff00 if it matches the background.
Edge requirement: asset edges must be cleanly separated from #00ff00. Repaint dirty white/gray/black edge residue, halos, labels, guide lines, screenshot residue, and card/tile backgrounds around the asset into exact #00ff00.
Important: a white or gray square/card behind an icon is background, not part of the asset.
Constraints: do not output transparent alpha. No labels, no watermark, no explanatory text, no borders, no grid lines.
```

For batching, AiClip groups by element type and size class and limits batches to 6 assets. The batch prompt must state exact asset count, grid rows/columns, same canvas size, one asset per cell, and no extra assets.

## Chroma Post-Processing

`scripts/process_chroma_icons.py` supports:

- `--manifest` using `cropSearchBBox` / `sheetBBox` cells;
- `--grid` + `--names` for simple grid sheets;
- `--key auto|none|green|magenta|#rrggbb`;
- tolerance/softness/despill controls;
- neutral/white background and icon halo removal for icon tiles;
- transparent trim plus padding.

Recommended AiClip parameters:

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

## HTML Reconstruction Rules

- Treat `source.png` dimensions as the base coordinate system.
- Use a fixed-size `position: relative` stage.
- Place extracted PNGs with `position:absolute; left/top/width/height` from `sourceBBox` or refined `htmlBBox`.
- Use `object-fit: contain` so trimmed transparent PNGs fit the original asset bbox.
- Code text, panels, cards, shadows, borders, radius, and simple backgrounds in CSS.
- Avoid icon libraries or recreated SVGs when a package asset exists.
- Verify by screenshotting HTML at source image dimensions and comparing to `source.png`.
