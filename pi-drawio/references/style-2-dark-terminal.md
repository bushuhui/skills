# Style 2: Dark Terminal

Neon-on-dark hacker aesthetic. Popular for dev blogs and GitHub README.

## Colors

```
Background:     #0f0f1a (use background rect)
Panel fill:     #0f172a (slate-950)
Panel stroke:   #334155 (slate-700)
Box radius:     arcSize=12

Text primary:   #e2e8f0 (slate-200)
Text secondary: #94a3b8 (slate-400)
Text muted:     #475569 (slate-600)

Accent palette (use per theme/layer):
  Purple:   fillColor=#1e1b4b;strokeColor=#7c3aed;
  Orange:   fillColor=#1c1917;strokeColor=#ea580c;
  Blue:     fillColor=#1e3a5f;strokeColor=#3b82f6;
  Green:    fillColor=#052e16;strokeColor=#059669;
  Gold:     strokeColor=#eab308;
  Red:      strokeColor=#dc2626;

Arrow colors: match accent of the source node
```

## draw.io Style Strings

### Background Rect
```
rounded=0;whiteSpace=wrap;html=1;fillColor=#0f0f1a;strokeColor=none;
```

### Standard Node
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#0f172a;strokeColor=#334155;arcSize=12;fontColor=#e2e8f0;fontSize=13;fontFamily=SF Mono, Fira Code, Cascadia Code, Courier New, Microsoft YaHei, SimHei, monospace;
```

### AI/ML Node (Purple)
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#1e1b4b;strokeColor=#7c3aed;arcSize=12;fontColor=#e2e8f0;fontSize=13;fontFamily=SF Mono, Fira Code, Cascadia Code, Courier New, Microsoft YaHei, SimHei, monospace;
```

### Compute/API Node (Orange)
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#1c1917;strokeColor=#ea580c;arcSize=12;fontColor=#e2e8f0;fontSize=13;fontFamily=SF Mono, Fira Code, Cascadia Code, Courier New, Microsoft YaHei, SimHei, monospace;
```

### Storage/DB Node (Green)
```
shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#052e16;strokeColor=#059669;fontColor=#e2e8f0;fontSize=13;fontFamily=SF Mono, Fira Code, Cascadia Code, Courier New, Microsoft YaHei, SimHei, monospace;
```

### Network Node (Blue)
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#1e3a5f;strokeColor=#3b82f6;arcSize=12;fontColor=#e2e8f0;fontSize=13;fontFamily=SF Mono, Fira Code, Cascadia Code, Courier New, Microsoft YaHei, SimHei, monospace;
```

### Container (Swimlane)
```
swimlane;startSize=30;whiteSpace=wrap;html=1;fillColor=#0f172a;strokeColor=#334155;fontColor=#94a3b8;fontSize=11;fontFamily=SF Mono, Fira Code, Cascadia Code, Courier New, Microsoft YaHei, SimHei, monospace;
```

### Edge (Purple - Default)
```
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#a855f7;strokeWidth=1.5;fontColor=#94a3b8;fontSize=11;
```

### Edge (Orange)
```
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#ea580c;strokeWidth=1.5;fontColor=#94a3b8;fontSize=11;
```

### Edge (Green)
```
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#10b981;strokeWidth=1.5;fontColor=#94a3b8;fontSize=11;
```

## Typography

```
fontFamily: SF Mono, Fira Code, Cascadia Code, Courier New, Microsoft YaHei, SimHei, monospace
fontSize:   13px labels, 11px sub-labels, 15px titles
fontStyle:  0 normal, 1 bold for section headers
```
