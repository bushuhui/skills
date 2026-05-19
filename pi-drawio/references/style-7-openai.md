# Style 7: OpenAI Official

Clean, modern aesthetic matching OpenAI's documentation - minimal but precise.

## Color Palette

```
Background:     #ffffff (pure white)
Primary text:   #0d0d0d (near black)
Secondary text: #6e6e80 (muted gray)
Border:         #e5e5e5 (light gray)

Accent colors (reserved):
  Green accent:   #10a37f (OpenAI brand green)
  Blue accent:    #1d4ed8 (links, actions)
  Orange accent:  #f97316 (highlights, warnings)
  Gray accent:    #71717a (secondary elements)
```

## draw.io Style Strings

### Standard Node
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#e5e5e5;strokeWidth=1.5;arcSize=16;fontColor=#0d0d0d;fontSize=16;fontStyle=1;fontFamily=-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, PingFang SC, Microsoft YaHei, SimHei, sans-serif;
```

### Accent Node (Green Left Border)
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#10a37f;strokeWidth=1.5;arcSize=16;fontColor=#0d0d0d;fontSize=16;fontStyle=1;fontFamily=-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, PingFang SC, Microsoft YaHei, SimHei, sans-serif;
```

### Database Cylinder
```
shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#e5e5e5;strokeWidth=1.5;fontColor=#0d0d0d;fontSize=14;fontFamily=-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, PingFang SC, Microsoft YaHei, SimHei, sans-serif;
```

### Container (Dashed)
```
rounded=1;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#e5e5e5;strokeWidth=1;dashed=1;dashPattern=4 3;fontColor=#6e6e80;fontSize=12;fontStyle=1;fontFamily=-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, PingFang SC, Microsoft YaHei, SimHei, sans-serif;
```

### Edge (Default - Gray)
```
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#71717a;strokeWidth=1.5;fontColor=#6e6e80;fontSize=12;
```

### Edge (Primary - Green)
```
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#10a37f;strokeWidth=1.5;fontColor=#6e6e80;fontSize=12;
```

### Edge (Optional/Async - Dashed)
```
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#71717a;strokeWidth=1.5;dashed=1;dashPattern=4 3;fontColor=#6e6e80;fontSize=12;
```

## Typography

```
fontFamily: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, PingFang SC, Microsoft YaHei, SimHei, sans-serif
fontSize:   16px node labels, 13px descriptions, 12px arrow labels
fontStyle:  1 bold for titles, 0 normal for descriptions
```

## Layout Principles

- Precise, grid-aligned layout
- Snap all coordinates to 8px grid
- Consistent 100px horizontal spacing, 120px vertical
- Generous whitespace (40px+ margins)
- No decorative elements

## Design Philosophy

- Minimalism: white on white, only essential visual elements
- Precision: thin strokes, subtle rounding (arcSize=16), grid-aligned
- Clarity: content-first, no visual noise
- Brand consistency: #10a37f green used sparingly for primary flows

Avoid: shadows, gradients, colorful fills, thick borders, decorative elements, custom fonts
