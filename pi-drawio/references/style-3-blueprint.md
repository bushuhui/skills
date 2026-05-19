# Style 3: Blueprint

Engineering blueprint aesthetic with grid background and technical annotation style.

## Colors

```
Background:     #0a1628 (use background rect)
Panel fill:     #0d1f3c
Panel stroke:   #00b4d8 (cyan/teal)
Box radius:     rounded=0 (sharp corners for technical feel)

Text primary:   #caf0f8 (light cyan)
Text secondary: #90e0ef
Text label:     #00b4d8

Accent colors:
  Cyan:    #00b4d8 / #48cae4
  White:   #ffffff (key labels)
  Orange:  #f77f00 (warnings/alerts)
  Green:   #06d6a0 (success/active)
```

## draw.io Style Strings

### Background Rect
```
rounded=0;whiteSpace=wrap;html=1;fillColor=#0a1628;strokeColor=none;
```

### Standard Node
```
rounded=0;whiteSpace=wrap;html=1;fillColor=#0d1f3c;strokeColor=#00b4d8;fontColor=#caf0f8;fontSize=13;fontFamily=Courier New, Lucida Console, Microsoft YaHei, SimHei, monospace;
```

### Dashed Node (External/Optional)
```
rounded=0;whiteSpace=wrap;html=1;fillColor=#0d1f3c;strokeColor=#00b4d8;dashed=1;dashPattern=6 3;fontColor=#caf0f8;fontSize=13;fontFamily=Courier New, Lucida Console, Microsoft YaHei, SimHei, monospace;
```

### Warning Node (Orange)
```
rounded=0;whiteSpace=wrap;html=1;fillColor=#0d1f3c;strokeColor=#f77f00;fontColor=#caf0f8;fontSize=13;fontFamily=Courier New, Lucida Console, Microsoft YaHei, SimHei, monospace;
```

### Container (Swimlane)
```
swimlane;startSize=30;whiteSpace=wrap;html=1;fillColor=#0d1f3c;strokeColor=#00b4d8;fontColor=#48cae4;fontSize=10;fontStyle=1;fontFamily=Courier New, Lucida Console, Microsoft YaHei, SimHei, monospace;
```

### Edge (Cyan - Default)
```
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#00b4d8;strokeWidth=1;fontColor=#48cae4;fontSize=10;fontFamily=Courier New, Lucida Console, Microsoft YaHei, SimHei, monospace;
```

### Edge (Orange - Warning)
```
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#f77f00;strokeWidth=1;fontColor=#f77f00;fontSize=10;
```

### Edge (Green - Success)
```
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#06d6a0;strokeWidth=1;fontColor=#06d6a0;fontSize=10;
```

## Typography

```
fontFamily: Courier New, Lucida Console, Microsoft YaHei, SimHei, monospace
fontSize:   13px labels, 10px annotations, 16px title
fontStyle:  0 normal; titles use fontStyle=1
```

## Title Block

Add a title block in the bottom-right:
```xml
<mxCell id="title-block" value="SYSTEM ARCHITECTURE&#xa;Diagram Title" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#0d1f3c;strokeColor=#00b4d8;fontColor=#caf0f8;fontSize=10;fontStyle=1;align=center;verticalAlign=middle;fontFamily=Courier New, Lucida Console, Microsoft YaHei, SimHei, monospace;" vertex="1" parent="1">
  <mxGeometry x="700" y="530" width="240" height="60" as="geometry"/>
</mxCell>
```
