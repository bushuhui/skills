# Semantic Shape Templates

Ready-to-use draw.io mxCell XML templates for common semantic concepts. These translate the SVG patterns from fireworks-tech-graph into draw.io format.

## LLM / Model Node (Double Border)

Signals "intelligent" or "AI-powered" component.

```xml
<mxCell id="N" value="GPT-4o&#xa;8K context" style="rounded=1;whiteSpace=wrap;html=1;double=1;fillColor=#eff6ff;strokeColor=#2563eb;arcSize=16;fontColor=#111827;fontSize=14;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="160" height="60" as="geometry"/>
</mxCell>
```

For dark styles, swap: `fillColor=#1e1b4b;strokeColor=#7c3aed;fontColor=#e2e8f0;`

## Agent / Orchestrator (Hexagon)

Signals "active controller" or "autonomous agent".

```xml
<mxCell id="N" value="Agent" style="shape=hexagon;whiteSpace=wrap;html=1;fillColor=#9dd4c7;strokeColor=#4a4a4a;fontColor=#1a1a1a;fontSize=14;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="140" height="80" as="geometry"/>
</mxCell>
```

For dark styles: `fillColor=#1e1b4b;strokeColor=#a855f7;fontColor=#e2e8f0;`

## Memory - Short-Term (Dashed Border)

Signals "ephemeral" or "temporary" storage.

```xml
<mxCell id="N" value="Short-term&#xa;Context Window" style="rounded=1;whiteSpace=wrap;html=1;dashed=1;dashPattern=6 3;fillColor=#fff7ed;strokeColor=#d79b00;fontColor=#111827;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="160" height="60" as="geometry"/>
</mxCell>
```

For dark styles: `fillColor=#1c1917;strokeColor=#ea580c;fontColor=#e2e8f0;`

## Memory - Long-Term (Cylinder)

Signals "persistent" storage.

```xml
<mxCell id="N" value="Vector DB&#xa;768-dim embeddings" style="shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontColor=#111827;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="140" height="80" as="geometry"/>
</mxCell>
```

## Vector Store (Cylinder with Label)

Specialized for vector databases.

```xml
<mxCell id="N" value="Pinecone&#xa;768-dim | Cosine" style="shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#1C1C2E;strokeColor=#00D68F;fontColor=#ffffff;fontSize=12;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="140" height="80" as="geometry"/>
</mxCell>
```

## Tool / Function Call

Signals "executable tool" or "API function".

```xml
<mxCell id="N" value="Search Tool" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f0fdf4;strokeColor=#86efac;fontColor=#111827;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="140" height="50" as="geometry"/>
</mxCell>
```

## API Gateway (Hexagon, Smaller)

Signals "routing" or "gateway" component.

```xml
<mxCell id="N" value="API Gateway" style="shape=hexagon;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontColor=#111827;fontSize=13;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="160" height="60" as="geometry"/>
</mxCell>
```

## Queue / Stream (Wide Rect)

Signals "message queue" or "event stream".

```xml
<mxCell id="N" value="Kafka" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontColor=#111827;fontSize=13;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="200" height="40" as="geometry"/>
</mxCell>
```

## Document / File

```xml
<mxCell id="N" value="Report.pdf" style="shape=document;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontColor=#111827;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="70" as="geometry"/>
</mxCell>
```

## Browser / Web Client

```xml
<mxCell id="N" value="Browser" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontColor=#111827;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="140" height="60" as="geometry"/>
</mxCell>
```

Add browser dots as a sub-label: `value="Browser&#xa;● ● ●"`

## User / Human Actor

```xml
<mxCell id="N" value="User" style="shape=mxgraph.uml.actor;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontColor=#111827;fontSize=12;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="40" height="60" as="geometry"/>
</mxCell>
```

## Decision Diamond (Flowcharts)

```xml
<mxCell id="N" value="Condition?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontColor=#111827;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="160" height="80" as="geometry"/>
</mxCell>
```

## Swim Lane Container (Layer/Group)

```xml
<mxCell id="N" value="Service Layer" style="swimlane;startSize=30;whiteSpace=wrap;html=1;fillColor=#f9fafb;strokeColor=#d1d5db;fontColor=#6b7280;fontSize=12;" vertex="1" parent="1">
  <mxGeometry x="40" y="200" width="800" height="180" as="geometry"/>
</mxCell>
```

Children inside use `parent="N"` and coordinates relative to container.

## Reasoning Loop (Curved Feedback Arrow)

```xml
<mxCell id="E" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;curved=1;strokeColor=#7c3aed;strokeWidth=1.5;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="agent" target="llm">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```
