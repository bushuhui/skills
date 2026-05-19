# Style 4: Notion Clean

Minimal, documentation-friendly. Designed to embed in Notion, Confluence, or GitHub wikis.

## Colors

```
Background:     #ffffff
Box fill:       #f9fafb (gray-50) or #ffffff
Box stroke:     #e5e7eb (gray-200)
Box radius:     arcSize=8

Text primary:   #111827 (gray-900)
Text secondary: #374151 (gray-700)
Text muted:     #9ca3af (gray-400)
Text label:     #6b7280 (gray-500), uppercase, 11px

Accent (subtle, used sparingly):
  Blue:   strokeColor=#3b82f6 (arrows only)
  Gray:   strokeColor=#d1d5db (dividers)
```

## Design Principles

- No decorative icons - use geometric shapes only
- Generous whitespace - 24px+ padding between elements
- Single arrow color - blue (#3b82f6) for all connections
- Labels in ALL CAPS - section headers and node type labels
- No drop shadows - flat only

## draw.io Style Strings

### Standard Node
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#f9fafb;strokeColor=#e5e7eb;arcSize=8;fontColor=#111827;fontSize=14;fontFamily=-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica Neue, Arial, PingFang SC, Microsoft YaHei, SimHei, sans-serif;
```

### Container (Dashed)
```
rounded=1;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#e5e7eb;dashed=1;dashPattern=4 3;fontColor=#9ca3af;fontSize=11;fontStyle=1;
```

### Database Cylinder
```
shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#f9fafb;strokeColor=#e5e7eb;fontColor=#111827;fontSize=14;fontFamily=-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica Neue, Arial, PingFang SC, Microsoft YaHei, SimHei, sans-serif;
```

### Edge (Primary)
```
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#3b82f6;strokeWidth=1.5;fontColor=#6b7280;fontSize=11;
```

### Edge (Secondary)
```
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#d1d5db;strokeWidth=1;dashed=1;dashPattern=4 3;fontColor=#9ca3af;fontSize=11;
```

## Typography

```
fontFamily: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica Neue, Arial, PingFang SC, Microsoft YaHei, SimHei, sans-serif
fontSize:   14px labels, 11px uppercase type labels, 18px title
fontStyle:  0 normal, 1 bold for titles
```

## Sizing Guide

- Node box: min 120x40, prefer 160x48 for readability
- Title: top-left, 18px, gray-900, margin 32px from edges
- Spacing: 80px minimum between nodes horizontally, 60px vertically
