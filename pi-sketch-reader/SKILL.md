---
name: pi-sketch-reader
description: >-
  Read and analyze UI sketch/design images (PNG, JPG, WEBP, SVG) and produce
  structured text descriptions with 6-dimension analysis. Trigger on:
  "analyze sketch" "read design" "describe mockup" "analyze UI image"
  "sketch analysis" "design review" or when user provides a UI/design image
  and wants structured analysis.
---

# Sketch Reader

Read UI sketch/design images and produce structured, detailed text descriptions.
Uses a vision-capable model to analyze layout, components, interactions, colors,
and typography. Outputs both human-readable Markdown and machine-readable JSON.

## When to Use

- User provides a UI sketch, mockup, or design image and wants analysis
- User says "analyze this design" or "describe this mockup"
- User needs structured design token extraction from an image
- User wants to compare multiple design variants
- User needs to bridge visual design into text-based planning or documentation

## Input

The user provides:
- **IMAGE_PATHS** — one or more image file paths (PNG, JPG, JPEG, WEBP, SVG, BMP, GIF)
- **OUTPUT_DIR** — where to write output (default: `./sketch-analysis/`)
- **SKETCH_NAME** — optional name for this sketch set (default: derived from first image filename)
- **CONTEXT_HINT** — optional hint about what the sketch represents (e.g., "login screen", "dashboard layout")

## Workflow

### Step 1: Parse Input

Identify from the user's message:
- All image paths provided
- Output directory (default: `./sketch-analysis/`)
- Sketch name (default: first image filename without extension)
- Context hint (default: none)

If image paths use glob patterns, expand them with the Glob tool.

Validate:
- At least one image must be provided
- Each path must point to a supported image format: `.png`, `.jpg`, `.jpeg`, `.webp`, `.svg`, `.bmp`, `.gif`

### Step 2: Read Images

For each image path:
1. Use the Read tool to load the image (Read supports images and returns them as attachments)
2. If a file doesn't exist or isn't a supported format, record it as `SKIPPED` with the reason
3. Track the order — descriptions reference images by index for traceability

### Step 3: Analyze Images

For each successfully loaded image, produce analysis across **6 dimensions**.
See `references/analysis-dimensions.md` for the full framework.

The dimensions are:
1. **Layout Structure** — overall pattern, regions, responsive hints, spacing
2. **Components & UI Elements** — type, position, labels, states, grouping
3. **Interaction & Navigation** — clickable elements, navigation patterns, modals, forms
4. **Color & Typography** — colors (hex if identifiable), font hierarchy, styles
5. **Data & Content** — data types, organization, empty states, pagination
6. **Annotations & Notes** — handwritten annotations, crossed-out elements, markers

### Step 4: Synthesize Description

Combine all image analyses into a single cohesive document. If multiple images
represent the same screen at different states or sizes, group them together.

Use the output template in `references/output-template.md`.

### Step 5: Write Output

Create the output directory if it doesn't exist.

Write two files:
1. **`{OUTPUT_DIR}/{SKETCH_NAME}-analysis.md`** — full structured analysis
2. **`{OUTPUT_DIR}/{SKETCH_NAME}-summary.json`** — machine-readable JSON summary

Use the Write tool for file creation. See `references/output-template.md` for
exact formats.

### Step 6: Report

Present a brief summary to the user:

```
Analyzed: {N} images → {M} screens
Analysis: {OUTPUT_DIR}/{SKETCH_NAME}-analysis.md
Summary:  {OUTPUT_DIR}/{SKETCH_NAME}-summary.json
```

If any images were skipped, list them with reasons.

## Anti-Patterns

Do NOT:
- Guess at functionality not indicated by the sketch — describe what you SEE, not what you assume
- Skip any of the 6 analysis dimensions even if the sketch is simple — note "N/A" or "none visible"
- Include your own design opinions or suggestions — you are an observer, not a designer
- Output raw image data or base64 — only text descriptions
- Fabricate content for elements that are too small or blurry to read — note them as "illegible"
- Ignore annotations — handwritten notes are often the most important part of a sketch
- Process more than 20 images per invocation (quality degrades with too many)

## Integration Tips

The JSON summary can be consumed by:
- Other skills or agents that need design context
- Automated design-to-code pipelines
- Design system documentation generators
- Any workflow that bridges visual design to text-based tooling

## Success Criteria

- [ ] All 6 analysis dimensions covered per screen
- [ ] One `.md` analysis file written to OUTPUT_DIR
- [ ] One `.json` summary file written to OUTPUT_DIR with valid schema
- [ ] Skipped images documented with reasons
- [ ] Cross-screen patterns described when multiple images provided
- [ ] Design tokens extracted when identifiable
