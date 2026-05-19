# Style 6: Claude Official

Inspired by Anthropic's Claude blog technical diagrams - warm, approachable, professional.

## Colors

```
Background:     #f8f6f3 (warm cream)

Semantic node colors:
  Input/Source:    fillColor=#a8c5e6;strokeColor=#4a4a4a; (soft blue)
  Agent/Process:   fillColor=#9dd4c7;strokeColor=#4a4a4a; (soft teal-green)
  Infrastructure:  fillColor=#f4e4c1;strokeColor=#4a4a4a; (warm beige)
  Storage/State:   fillColor=#e8e6e3;strokeColor=#4a4a4a; (light gray)

Arrow color:     strokeColor=#5a5a5a (consistent dark gray)
```

## draw.io Style Strings

### Agent Node (Teal-Green)
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#9dd4c7;strokeColor=#4a4a4a;strokeWidth=2.5;arcSize=24;fontColor=#1a1a1a;fontSize=16;fontStyle=1;shadow=1;fontFamily=-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica Neue, Arial, PingFang SC, Microsoft YaHei, SimHei, sans-serif;
```

### Input/Source Node (Soft Blue)
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#a8c5e6;strokeColor=#4a4a4a;strokeWidth=2.5;arcSize=24;fontColor=#1a1a1a;fontSize=16;fontStyle=1;shadow=1;fontFamily=-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica Neue, Arial, PingFang SC, Microsoft YaHei, SimHei, sans-serif;
```

### Infrastructure Node (Beige)
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#f4e4c1;strokeColor=#4a4a4a;strokeWidth=2.5;arcSize=24;fontColor=#1a1a1a;fontSize=16;fontStyle=1;shadow=1;fontFamily=-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica Neue, Arial, PingFang SC, Microsoft YaHei, SimHei, sans-serif;
```

### Storage/State Node (Gray)
```
shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#e8e6e3;strokeColor=#4a4a4a;strokeWidth=2.5;fontColor=#1a1a1a;fontSize=16;fontStyle=1;shadow=1;fontFamily=-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica Neue, Arial, PingFang SC, Microsoft YaHei, SimHei, sans-serif;
```

### Background Rect
```
rounded=0;whiteSpace=wrap;html=1;fillColor=#f8f6f3;strokeColor=none;
```

### Edge (Read/Primary)
```
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#5a5a5a;strokeWidth=2;fontColor=#5a5a5a;fontSize=13;
```

### Edge (Write)
```
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#5a5a5a;strokeWidth=2;dashed=1;dashPattern=5 3;fontColor=#5a5a5a;fontSize=13;
```

### Edge (Control)
```
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#5a5a5a;strokeWidth=1.5;dashed=1;dashPattern=3 2;fontColor=#5a5a5a;fontSize=13;
```

## Typography

```
fontFamily: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica Neue, Arial, PingFang SC, Microsoft YaHei, SimHei, sans-serif
fontSize:   16px node labels, 14px descriptions, 13px arrow labels
fontStyle:  1 bold for node labels, 0 normal for descriptions
```

## Node Content Guidelines

Node content should include technical details, not just concepts:
- Line 1: Component name (bold, 16px)
- Line 2: Technical detail or implementation (14px)
- Line 3: Key parameter or constraint (14px, optional)

Use &#xa; for multi-line labels: `value="Vector Store&#xa;768-dim embeddings&#xa;Cosine similarity"`

## Legend

When using 2+ arrow types, include a legend in the bottom-right:
```xml
<mxCell id="legend" value="Legend" style="swimlane;startSize=20;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#4a4a4a;strokeWidth=1.5;fontColor=#1a1a1a;fontSize=13;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="720" y="520" width="220" height="80" as="geometry"/>
</mxCell>
```
