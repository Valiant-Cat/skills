# Reference Style System

This reference distills the visual language from `assets/reference-icon-grid.jpeg`, a 40-icon grid of polished app icons and mascots.

## Extracted Design DNA

The grid uses a consistent preview formula:

- Rounded-square app tile with large corner radius.
- Smooth high-saturation gradient background, often blue, teal, purple, orange, green, or pink.
- One centered 3D subject, usually an object with a face or a mascot with one prop.
- Toy-like geometry: inflated forms, bevels, soft edges, large simple volumes.
- Minimal kawaii facial language: glossy black oval eyes, small smile, occasional blush or tiny mouth.
- High depth polish: soft contact shadow, ambient occlusion, upper-left highlight, rim light, subtle inner glow.
- Category symbol is instantly readable: robot, piggy bank, camera, heart, owl, shield, moon, rocket, palette, microphone, compass.
- Decorative details are sparse: stars, music notes, check marks, drops, map folds, coins, sparkles.
- Each icon has strong contrast between subject and tile, making it readable on a phone screen.

For project use, reinterpret this formula as a transparent production mascot/icon first: keep the central subject, material, lighting, and polish, but remove the rounded-square tile into real alpha. Generate a separate gradient rounded-square tile only for App Store preview, marketing display, or when the user explicitly asks for a tiled app icon.

## Visual Motifs Observed

Subjects in the reference fall into repeatable families:

- **Cute tech/helper**: robot, microphone, camera, game controller, battery.
- **Friendly finance/commerce**: piggy bank with coin, treasure chest, shopping bag.
- **Learning/productivity**: clipboard, owl graduate, notebook, document, lightbulb.
- **Wellness/emotion**: meditating cloud, running heart, moon, sun/cloud, water drop, plant.
- **Travel/location**: suitcase with sunglasses, map pin, compass.
- **Food/lifestyle**: noodle bowl, chef, llama, dog.
- **Communication/media**: headphones penguin, chat owl, envelope.

## Shape Language

Use these shape choices:

- Large primary blob/rounded form for instant recognition.
- Short tiny limbs only when they add energy or friendliness.
- Oversized accessories, simplified enough to read at icon size.
- Deep bevels and rounded seams on objects like shields, suitcases, books, batteries, and controllers.
- Squash-and-stretch proportions: big head/body, tiny arms/legs, compact posture.
- Avoid thin linework. Make every contour chunky.

## Material Language

Choose one dominant material per icon:

- **Glossy plastic**: tech, camera, controller, battery, robot.
- **Soft clay**: heart, water drop, cloud, sun, moon, map pin.
- **Plush/fleece**: animals, llama, penguin, dog.
- **Enamel/toy metal**: compass, shield, microphone, bell.
- **Ceramic/porcelain**: bowl, plant pot.

Material treatment:

- Add broad soft highlights, not sharp chrome reflections.
- Use ambient occlusion in creases and where accessories touch the body.
- Use subtle texture only for plush or food; most objects should be smooth.
- Preserve clean edges and a premium rendered finish.

## Color Recipes

Good combinations inspired by the grid:

- Cyan/blue background + white robot or cloud + electric blue eye accents.
- Green background + pink pig or purple shopping bag + gold accent.
- Orange background + yellow character, red heart, or cream food.
- Purple background + yellow moon, owl, book, or microphone accent.
- Teal background + white plant pot, green leaves, turquoise object.
- Blue background + red/white rocket, shield, compass, or envelope.
- Pink/magenta background + white microphone or camera body.

Keep palettes vivid but balanced. Do not make every element the same hue. For transparent production files, apply the contrast through the subject and accents. For optional tile previews, use one dominant background family, one contrasting subject color, and one small accent.

## Composition Formula

Use this layout ratio for most icons:

- Production canvas: 100%, transparent.
- Optional preview tile: 100%, rounded-square gradient.
- Safe padding: 9-14%.
- Subject bounding box: 68-82%.
- Face zone: about 8-18% of tile width.
- Accessory cue: 10-25%, placed near top corner or side of subject.
- Shadow footprint: 35-60% of subject width, soft and darkened by 15-30%.

Use front view for trust and friendliness. Use slight 3/4 angle for physical objects that benefit from depth, such as cameras, suitcases, books, and compasses.

## Lighting Formula

- Key light: upper-left, large softbox.
- Fill: gentle front fill to keep face bright.
- Rim light: subtle edge glow on top/right side.
- Contact shadow: directly under subject, blurred, never harsh.
- Background glow: use only in tile preview; for transparent production files, use subject rim light instead of background glow.
- Add tiny sparkles only when magic, success, or delight is part of the concept.

## Transparent Production Default

Default deliverables should be PNG/WebP with real alpha:

- All four corners must be alpha transparent.
- No black corners, white corners, or fake checkerboard background.
- No visible chroma-key halo around the subject.
- No cast shadow that depends on a colored tile unless a grounded shadow is explicitly desired and preserved as semi-transparent pixels.
- The subject should remain complete and visually balanced without a background tile.

For GPT-Image-2/built-in imagegen, use a flat chroma-key source and local background removal:

```text
Create the subject on a perfectly flat solid chroma-key background for removal. Use a key color that does not appear in the subject. The background must be completely uniform, with no shadow, no gradient, no texture, no reflections, and no lighting variation. Keep the subject fully separated from the key color with crisp antialiased edges and generous padding.
```

After removal, inspect alpha corners and edge quality before delivering. If the subject color conflicts with green, use magenta; if it conflicts with both, choose another high-contrast flat key. Validate every transparent deliverable with:

```bash
python3 scripts/validate_alpha_corners.py <icon.png>
```

## Ideation Method

When given an app concept:

1. Name the user promise in two words: calm focus, safer money, smarter travel, quick learning, joyful fitness.
2. Choose one instantly recognizable noun for the subject.
3. Decide whether it should be an object-character, animal mascot, or symbolic object.
4. Add one accessory cue that explains the app category.
5. Pick a contrasting palette from the recipes above.
6. Assign an emotion: cheerful, calm, proud, curious, energetic, sleepy, helpful.
7. Write a prompt that describes visible form, material, lighting, and background.

## Prompt Enhancers

Use these phrases selectively:

- "premium 3D mobile app icon"
- "toy-like soft clay and glossy plastic finish"
- "rounded inflated forms, tactile bevels"
- "tiny glossy black eyes and a simple friendly smile"
- "smooth saturated gradient rounded-square tile"
- "transparent production PNG/WebP with true alpha corners"
- "large centered subject, clear silhouette at 64px"
- "upper-left soft studio light, rim glow, ambient occlusion"
- "subtle contact shadow, app-store-ready polish"

## Negative Prompt Ideas

Include these when imagegen tends to overcomplicate:

```text
No text, no letters, no numbers, no watermark, no photorealistic human hands, no complex background scene, no flat vector style, no harsh outlines, no gritty texture, no clutter, no extra characters, no malformed limbs, no scary expression, no black corners, no white corners, no fake checkerboard transparency.
```

## Example Concepts

### Privacy app

Transparent smiling blue shield with glossy beveled edge, tiny face, silver rim, and one small sparkle. Optional preview tile: cyan gradient. Emotion: trustworthy and friendly.

### Habit tracker

Transparent happy checklist clipboard holding an oversized pencil, green check accents, soft plastic material. Optional preview tile: clean blue gradient. Emotion: helpful and organized.

### Meditation app

Transparent sleepy lavender cloud sitting cross-legged, closed eyes, tiny stars, soft clay material. Optional preview tile: purple-to-indigo gradient. Emotion: calm and cozy.

### Travel planner

Transparent turquoise suitcase with sunglasses and straw hat, tiny luggage wheels, glossy plastic finish. Optional preview tile: warm cyan gradient. Emotion: playful and ready.

### Finance app

Transparent pink piggy bank with gold coin, rounded toy plastic material, confident smile. Optional preview tile: green gradient. Emotion: safe and rewarding.

### AI assistant app

Transparent white rounded robot head/body with black glossy face screen, cyan glowing eyes, soft rim light. Optional preview tile: blue gradient. Emotion: smart and approachable.
