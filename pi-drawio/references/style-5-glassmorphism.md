# Style 5: Glassmorphism

Frosted glass cards on dark gradient. Designed for product sites, keynotes, and hero sections.

## Colors

```
Background gradient: #0d1117 -> #161b22 -> #0d1117 (use background rect with gradient)

Glass card:
  fill:           fillColor=#161b22;fillOpacity=20;
  stroke:         strokeColor=#ffffff;strokeOpacity=15;
  box-radius:     arcSize=24

Text primary:   #f0f6fc (near-white)
Text secondary: #8b949e (muted)

Accent glows (one per layer):
  Blue glow:    fillColor=#1e3a5f;fillOpacity=30;strokeColor=#58a6ff;
  Purple glow:  fillColor=#2d1b4e;fillOpacity=30;strokeColor=#bc8cff;
  Green glow:   fillColor=#0d2818;fillOpacity=30;strokeColor=#3fb950;
  Orange glow:  fillColor=#2d1810;fillOpacity=30;strokeColor=#f78166;
```

## draw.io Style Strings

### Background Rect (Gradient)
```
rounded=0;whiteSpace=wrap;html=1;fillColor=#0d1117;gradientColor=#161b22;gradientDirection=south;strokeColor=none;
```

### Standard Node (Glass)
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#161b22;fillOpacity=20;strokeColor=#ffffff;strokeOpacity=15;arcSize=24;fontColor=#f0f6fc;fontSize=14;shadow=1;fontFamily=Inter, -apple-system, SF Pro Display, PingFang SC, Microsoft YaHei, SimHei, sans-serif;
```

### Blue Glow Node
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#1e3a5f;fillOpacity=30;strokeColor=#58a6ff;arcSize=24;fontColor=#f0f6fc;fontSize=14;shadow=1;fontFamily=Inter, -apple-system, SF Pro Display, PingFang SC, Microsoft YaHei, SimHei, sans-serif;
```

### Purple Glow Node
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#2d1b4e;fillOpacity=30;strokeColor=#bc8cff;arcSize=24;fontColor=#f0f6fc;fontSize=14;shadow=1;fontFamily=Inter, -apple-system, SF Pro Display, PingFang SC, Microsoft YaHei, SimHei, sans-serif;
```

### Container (Swimlane)
```
swimlane;startSize=30;whiteSpace=wrap;html=1;fillColor=#161b22;fillOpacity=10;strokeColor=#ffffff;strokeOpacity=10;fontColor=#8b949e;fontSize=11;fontFamily=Inter, -apple-system, SF Pro Display, PingFang SC, Microsoft YaHei, SimHei, sans-serif;
```

### Edge (Blue Glow)
```
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#58a6ff;strokeWidth=1.5;opacity=80;fontColor=#8b949e;fontSize=11;
```

### Edge (Purple Glow)
```
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#bc8cff;strokeWidth=1.5;opacity=80;fontColor=#8b949e;fontSize=11;
```

## Typography

```
fontFamily: Inter, -apple-system, SF Pro Display, PingFang SC, Microsoft YaHei, SimHei, sans-serif
fontSize:   14px labels, 12px sublabels, 20px hero title
fontStyle:  0 normal, 1 bold titles
```

## Notes

- draw.io has limited glassmorphism support; low opacity fills + shadow approximate the effect
- Use shadow=1 on key nodes for depth
- Gradient backgrounds work well in draw.io desktop and exports
