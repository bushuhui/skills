# Draw.io Layout Best Practices

Universal layout rules adapted for draw.io XML generation. Apply these on top of the style-specific rules from `style-N.md` references.

## Universal Layout Rules

### 1. Component Spacing

| Complexity | Nodes | Horizontal Gap | Vertical Gap | Routing Corridor |
|-----------|-------|----------------|--------------|-----------------|
| Simple | <=5 | 200px | 150px | 80px |
| Medium | 6-10 | 280px | 200px | 80px |
| Complex | >10 | 350px | 250px | 100px |

- **Routing corridor**: between shape rows/columns, leave an extra 80-100px empty corridor where edges can route without crossing shapes. Never place a shape in a gap that edges need to traverse.
- **Grid alignment**: snap all `x`, `y`, `width`, `height` values to multiples of 10. This ensures shapes align cleanly on draw.io's default grid.

### 2. Connection Point Rules

When multiple edges connect to the same shape, distribute entry/exit points:

| Position | exitX/entryX | exitY/entryY | Use When |
|----------|-------------|-------------|----------|
| Top center | 0.5 | 0 | Connecting to node above |
| Top-left | 0.25 | 0 | 2nd connection from top |
| Top-right | 0.75 | 0 | 3rd connection from top |
| Right center | 1 | 0.5 | Connecting to node on right |
| Bottom center | 0.5 | 1 | Connecting to node below |
| Bottom-left | 0.25 | 1 | 2nd connection from bottom |
| Bottom-right | 0.75 | 1 | 3rd connection from bottom |
| Left center | 0 | 0.5 | Connecting to node on left |

**Rules:**
- Never connect arrows to shape corners - use midpoints of edges
- If a shape has N connections on one side, space them evenly (3 connections on bottom -> exitX = 0.25, 0.5, 0.75)
- Minimum clearance from corners: use x/y offsets of at least 0.15 (15% from edge)
- Pin `exitX/exitY/entryX/entryY` on every edge when a node has 2+ connections

### 3. Arrow Label Rules

Arrow labels are critical for readability. Always apply these rules when edges carry labels:

| Rule | draw.io Implementation |
|------|----------------------|
| Labels MUST have background | Add `labelBackgroundColor=#ffffff;` (or match your style's background color) to edge style |
| Position | Labels appear at midpoint by default; use `labelPosition` / `align` to fine-tune |
| Keep short | <=3 words on arrow labels; put detail in node labels |
| Multiple converging arrows | Stagger label positions by assigning different exit/entry points |
| Safety distance | Keep label text 10px+ from any shape edge |

Example edge with label background:
```xml
<mxCell id="E1" value="HTTP/REST" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;labelBackgroundColor=#ffffff;strokeColor=#2563eb;strokeWidth=1.5;" edge="1" parent="1" source="2" target="3">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

For dark styles (2, 3, 5), match the background:
```
labelBackgroundColor=#0f0f1a;   (Style 2 Dark Terminal)
labelBackgroundColor=#0a1628;   (Style 3 Blueprint)
labelBackgroundColor=#0d1117;   (Style 5 Glassmorphism)
```

### 4. Arrow Routing

| Scenario | Strategy |
|----------|----------|
| Straight line, clear path | Default orthogonal routing (no waypoints needed) |
| Edge must detour around shape | Add `<Array as="points">` waypoints |
| Edge crosses unrelated shape | Move the shape, increase spacing, or add waypoints to route around |
| Multiple edges between same layers | Stagger by using different exit/entry X or Y values |
| Long cross-layer edge | Route along the outer corridor, not through the middle |
| Feedback/loop arrow | Use `curved=1;` for smooth arc instead of orthogonal corners |

**Arrowhead clearance**: the final straight segment between the last bend and the target shape must be >=20px long. If too short, the arrowhead overlaps the bend and looks broken.

### 5. Z-Index (Render Order)

In draw.io XML, the order of `mxCell` elements determines rendering layer (later elements render on top). Follow this order:

1. Background rect (for dark/colored backgrounds)
2. Container shapes (`swimlane`, dashed grouping rects)
3. Edge (arrow) elements
4. Vertex (node) shapes
5. Legend containers

This ensures:
- Arrows route behind nodes
- Nodes don't get obscured by containers
- Background stays behind everything

### 6. Overlap Detection Checklist

Before finalizing the diagram, verify:

| Check | Method | Fix |
|-------|--------|-----|
| Shape overlap | No two shape bounding boxes overlap (with 20px margin) | Increase spacing or move shapes |
| Arrow-shape collision | No edge path visually passes through an unrelated shape | Add waypoints or increase spacing |
| Label overlap | No arrow label overlaps with a node or another label | Add `labelBackgroundColor`, adjust exit/entry points, or stagger labels |
| Off-canvas shapes | All shapes have positive x/y coordinates within reasonable range | Move shapes to positive coordinates |
| Container overflow | Children do not exceed parent container bounds | Increase container width/height |

## Layout Patterns by Diagram Type

### Hub / Star Layout
- Place hub node centrally
- Satellite nodes evenly distributed around it
- Connect with short radial arrows
- Avoid arrows crossing between satellites

### Tree / Hierarchical Layout
- Assign nodes to layers (rows)
- Connect only between adjacent layers to minimize crossings
- Parent centered above children (same center x)
- Use swimlanes for layer grouping

### Ring / Cycle Layout
- Nodes distributed on a circle (use trigonometry for x/y)
- Edges follow the ring or span across with curved arrows
- Center x = total_width/2, center y = total_height/2
- Radius = min(width, height) * 0.35

### Grid / Matrix Layout
- Fixed column width and row height
- Use `shape=table;` for structured data
- Alternating row fills for readability
- Max 5 readable columns; split if more needed

## Style-Specific Layout Notes

### Style 1: Flat Icon
- Snap all coordinates to 10px grid
- Consistent rounded corners: `arcSize=16`
- Thin arrows (1.5px), filled arrowheads
- No shadows - flat design principle

### Style 2: Dark Terminal
- Background rect required (`fillColor=#0f0f1a`)
- Monospace font for code-like feel
- Colored borders distinguish node types on dark background
- Glow effect: use brighter strokeColor than fillColor

### Style 3: Blueprint
- Background rect required (`fillColor=#0a1628`)
- Monospace font for technical/engineering feel
- No rounded corners: `rounded=0`
- Dashed borders for external/unknown components

### Style 5: Glassmorphism
- Gradient background rect required
- Low fillOpacity (20-30) for glass effect
- Shadow on key nodes: `shadow=1;`
- Rounded corners: `arcSize=24`

### Style 6: Claude Official
- Warm cream background rect (`fillColor=#f8f6f3`)
- Thicker strokes (strokeWidth=2.5) for bold look
- Shadow on all nodes: `shadow=1;`
- Rounded corners: `arcSize=24`

## Validation Checklist

Run through this list before exporting:

- [ ] No arrow-shape overlaps (arrows route through gaps, not through shape interiors)
- [ ] All arrow labels have `labelBackgroundColor` matching the style background
- [ ] Minimum 80px clearance for all arrow routing corridors
- [ ] Component spacing follows complexity scale (200-350px horizontal, 150-250px vertical)
- [ ] Arrow connection points avoid corners (use midpoints with offsets)
- [ ] Multiple arrows between same layers are staggered via different exit/entry points
- [ ] Z-Index order is correct (background -> containers -> edges -> nodes -> legend)
- [ ] Legend is readable and doesn't overlap content
- [ ] Dark background styles have background rect cell
- [ ] All edge cells have `<mxGeometry relative="1" as="geometry"/>` child element
- [ ] No self-closing edge cells
- [ ] All `id` values are unique and sequential from 2
- [ ] Special characters in `value` are XML-escaped

## Common Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| Arrow crosses component interior | Add waypoints to route around; or increase spacing |
| Arrow label unreadable over line | Add `labelBackgroundColor` to edge style |
| Components too close | Increase spacing to complexity-scale minimums |
| Arrow connects to corner | Move connection point to edge midpoint with offset |
| No z-index planning | Follow render order: background -> containers -> edges -> nodes -> legend |
| Dark background missing | Add background rect cell as first element after id="1" |
| All edges exit same point | Distribute exit/entry points across shape perimeter |
| Labels overlap at convergence | Stagger label positions via different exit/entry points |
