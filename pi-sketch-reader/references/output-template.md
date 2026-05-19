# Output Templates

## Markdown Analysis Template

Use this structure for the `-analysis.md` file:

    # Sketch Analysis: {SKETCH_NAME}

    ## Overview
    {2-3 sentence summary of what the sketches depict, informed by CONTEXT_HINT if provided}

    ## Screens

    ### Screen 1: {inferred screen name}
    **Source:** {image filename}
    **Layout:** {layout pattern description}

    #### Structure
    {Numbered list of major sections/regions with their purpose}

    #### Components
    {Detailed component inventory with types, labels, positions}

    #### Interactions
    {Navigation and interaction patterns}

    #### Visual Design
    {Colors, typography, spacing}

    #### Annotations
    {Any handwritten notes, arrows, callouts}

    {Repeat for each screen/image}

    ## Cross-Screen Patterns
    {If multiple screens: shared navigation, consistent elements, flow between screens}

    ## Design Tokens (extracted)
    - **Primary color:** {hex or description}
    - **Background:** {hex or description}
    - **Font hierarchy:** {heading > body > caption sizes}
    - **Spacing:** {tight | normal | generous}
    - **Border radius:** {sharp | slight | rounded | pill}
    - **Shadow depth:** {none | subtle | medium | prominent}

## JSON Summary Template

Use this structure for the `-summary.json` file:

    {
      "sketch_name": "{SKETCH_NAME}",
      "image_count": {N},
      "images_skipped": [{ "path": "...", "reason": "..." }],
      "screens": [
        {
          "name": "inferred screen name",
          "source_image": "filename",
          "layout_pattern": "sidebar + main",
          "viewport_hint": "desktop",
          "component_count": {N},
          "has_navigation": true,
          "has_forms": false,
          "has_data_display": true,
          "annotations_detected": true
        }
      ],
      "design_tokens": {
        "primary_color": "...",
        "background": "...",
        "spacing": "normal",
        "border_radius": "rounded",
        "shadow_depth": "subtle"
      },
      "context_hint": "{CONTEXT_HINT if provided}"
    }

## Naming Conventions

- Analysis file: `{SKETCH_NAME}-analysis.md`
- Summary file: `{SKETCH_NAME}-summary.json`
- If name conflicts with existing files, append version suffix (e.g., `login-v2-analysis.md`)
