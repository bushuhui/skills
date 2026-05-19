# Style 1: Flat Icon (Default)

Inspired by draw.io defaults and Apple documentation style.

## Colors

```
Background:     #ffffff
Box fill:       #ffffff
Box stroke:     #d1d5db (gray-300)
Box radius:     arcSize=16
Text primary:   #111827 (gray-900)
Text secondary: #6b7280 (gray-500)

Icon accent backgrounds:
  Blue tint:   fillColor=#eff6ff;strokeColor=#bfdbfe;
  Red tint:    fillColor=#fef2f2;strokeColor=#fee2e2;
  Green tint:  fillColor=#f0fdf4;strokeColor=#86efac;
  Purple tint: fillColor=#faf5ff;strokeColor=#c4b5fd;
  Orange tint: fillColor=#fff7ed;strokeColor=#fed7aa;
  Teal tint:   fillColor=#f0fdfa;strokeColor=#ccfbf1;

Semantic arrow colors:
  Flow A (main):   strokeColor=#2563eb;
  Flow B (alt):    strokeColor=#dc2626;
  Flow C (data):   strokeColor=#16a34a;
  Flow D (async):  strokeColor=#9333ea;
```

## draw.io Style Strings

### Standard Node
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d1d5db;arcSize=16;fontColor=#111827;fontSize=14;fontFamily=Helvetica Neue, Helvetica, Arial, PingFang SC, Microsoft YaHei, SimHei, sans-serif;
```

### Accent Node (Blue)
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#eff6ff;strokeColor=#bfdbfe;arcSize=16;fontColor=#111827;fontSize=14;fontFamily=Helvetica Neue, Helvetica, Arial, PingFang SC, Microsoft YaHei, SimHei, sans-serif;
```

### Database Cylinder
```
shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#f0fdf4;strokeColor=#86efac;fontColor=#111827;fontSize=14;fontFamily=Helvetica Neue, Helvetica, Arial, PingFang SC, Microsoft YaHei, SimHei, sans-serif;
```

### Container (Swimlane)
```
swimlane;startSize=30;whiteSpace=wrap;html=1;fillColor=#f9fafb;strokeColor=#d1d5db;fontColor=#6b7280;fontSize=12;fontFamily=Helvetica Neue, Helvetica, Arial, PingFang SC, Microsoft YaHei, SimHei, sans-serif;
```

### Dashed Container (Grouping)
```
rounded=1;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#d1d5db;dashed=1;dashPattern=4 3;fontColor=#6b7280;fontSize=11;
```

### Edge (Primary)
```
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#2563eb;strokeWidth=1.5;
```

### Edge (Alternative)
```
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#dc2626;strokeWidth=1.5;
```

### Edge (Data Flow)
```
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#16a34a;strokeWidth=2.5;
```

### Edge (Async)
```
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#9333ea;strokeWidth=1.5;dashed=1;dashPattern=4 2;
```

### Legend Container
```
swimlane;startSize=20;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d1d5db;fontColor=#6b7280;fontSize=11;
```

## Typography

```
fontFamily: Helvetica Neue, Helvetica, Arial, PingFang SC, Microsoft YaHei, SimHei, sans-serif
fontSize:   14px labels, 12px sub-labels, 16px titles
fontStyle:  0 normal, 1 bold for titles
```
