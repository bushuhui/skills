# Diagram Type Presets

Detailed style reference for each diagram type. When the user requests a specific diagram type, apply the matching preset.

## 1. Architecture Diagram

| Element | Style | Notes |
|---------|-------|-------|
| Layer/tier | `swimlane;startSize=30;whiteSpace=wrap;html=1;` | Containers for grouping: Client / API / Service / Data |
| Service | `rounded=1;whiteSpace=wrap;html=1;` + tier color | Use color palette by tier |
| Database | `shape=cylinder3;whiteSpace=wrap;html=1;` | Green palette |
| Queue/Bus | `rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;` | Yellow - place centrally for hub pattern |
| Gateway/LB | `shape=mxgraph.aws4.resourceIcon;` or `rounded=1;` with orange | Orange palette |
| External | `rounded=1;dashed=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;` | Dashed border for external systems |
| Edge | `edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;` | Standard routing |
| Layout | TB or LR by tier count; 4+ tiers -> TB | Hub nodes centered in their row |

## 2. Data Flow Diagram

| Element | Style | Notes |
|---------|-------|-------|
| Process/Transform | `rounded=1;whiteSpace=wrap;html=1;` | Standard node |
| Data store | `shape=cylinder3;whiteSpace=wrap;html=1;` | Cylinder for persistence |
| Primary data edge | `edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2.5;` | Wider stroke for primary paths |
| Control edge | `edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;dashed=1;dashPattern=5 3;` | Dashed for triggers |
| Animated data flow | Add `flowAnimation=1;` to any edge style | Moving dot along arrow in draw.io desktop/SVG |
| Layout | TB, label every arrow with data type | Color arrows by data category |

## 3. Flowchart / Process Flow

| Element | Style | Notes |
|---------|-------|-------|
| Start/End | `ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;` | Green oval |
| Process | `rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;` | Blue rectangle |
| Decision | `rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;` | Yellow diamond |
| I/O | `shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;` | Orange parallelogram |
| Subprocess | `rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;` | Purple |
| Yes/No labels | `value="Yes"` / `value="No"` on decision edges | Always label decision branches |
| Edge | `edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;` | Standard |
| Layout | TB, 200px vertical gap | Decisions branch LR, merge back to center |

## 4. Agent Architecture Diagram

| Element | Style | Notes |
|---------|-------|-------|
| LLM/Model | `rounded=1;whiteSpace=wrap;html=1;double=1;` | Double border = "intelligent" |
| Agent/Orchestrator | `shape=hexagon;whiteSpace=wrap;html=1;` | Hexagon = active controller |
| Memory (short-term) | `rounded=1;whiteSpace=wrap;html=1;dashed=1;dashPattern=6 3;` | Dashed = ephemeral |
| Memory (long-term) | `shape=cylinder3;whiteSpace=wrap;html=1;` | Cylinder = persistent |
| Tool/Function | `rounded=1;whiteSpace=wrap;html=1;` | Standard rect with tool name |
| Reasoning loop | Add `curved=1;strokeColor=#7c3aed;` to edge style | Curved purple loop arrow |
| Container | `swimlane;startSize=30;whiteSpace=wrap;html=1;` | Layer grouping |
| Layout | TB by layers: Input -> Agent -> Memory -> Tool -> Output | Use `curved=1;` for feedback loops |

## 5. Memory Architecture Diagram

| Element | Style | Notes |
|---------|-------|-------|
| Working Memory | `rounded=1;whiteSpace=wrap;html=1;dashed=1;dashPattern=4 3;` | Short-lived |
| Short-term Memory | `rounded=1;whiteSpace=wrap;html=1;dashed=1;dashPattern=6 3;` | Ephemeral |
| Long-term Memory | `shape=cylinder3;whiteSpace=wrap;html=1;` | Persistent store |
| External Store | `shape=cylinder3;whiteSpace=wrap;html=1;dashed=1;dashPattern=6 3;` | External = dashed |
| Read path edge | `edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#059669;strokeWidth=1.5;` | Green = read |
| Write path edge | `edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#059669;strokeWidth=1.5;dashed=1;dashPattern=5 3;` | Green dashed = write |
| Layout | TB, stacked tiers for storage | Label ops: `store()`, `retrieve()`, `forget()` |

## 6. Sequence Diagram

| Element | Style | Notes |
|---------|-------|-------|
| Actor/Object | `shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;portConstraint=eastwest;` | Lifeline with dashed vertical line |
| Sync message | `html=1;verticalAlign=bottom;endArrow=block;` | Solid line, filled arrowhead |
| Async message | `html=1;verticalAlign=bottom;endArrow=open;dashed=1;` | Dashed line, open arrowhead |
| Return message | `html=1;verticalAlign=bottom;endArrow=open;dashed=1;strokeColor=#999999;` | Grey dashed |
| Activation box | `shape=umlFrame;whiteSpace=wrap;` on the lifeline | Narrow rectangle on lifeline |
| Loop/Alt frame | `shape=mxgraph.uml.fragment;whiteSpace=wrap;html=1;` | With label in top-left corner |
| Layout | LR, lifelines spaced 200px apart | Time flows top to bottom |

## 7. ER Diagram

| Element | Style | Notes |
|---------|-------|-------|
| Table | `shape=table;startSize=30;container=1;collapsible=1;childLayout=tableLayout;fixedRows=1;rowLines=0;fontStyle=1;strokeColor=#6c8ebf;fillColor=#dae8fc;` | Each table is a container |
| Row (column) | `shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;fontSize=12;` | Child of table, `parent=tableId` |
| PK column | Bold text: `fontStyle=1` on the row | Mark with `PK` prefix |
| FK relationship | `dashed=1;endArrow=ERmandOne;startArrow=ERmandOne;` | Use ER notation arrows |
| Cell (PK) | `shape=partialRectangle;top=0;left=0;right=0;bottom=1;fillColor=none;fontStyle=1;align=left;` | Bold for primary key |
| Cell | `shape=partialRectangle;top=0;left=0;right=0;bottom=1;fillColor=none;align=left;` | Normal column |
| Layout | TB, tables spaced 300px apart | Group related tables vertically |

## 8. UML Class Diagram

| Element | Style | Notes |
|---------|-------|-------|
| Class box | `swimlane;fontStyle=1;align=center;startSize=26;html=1;` | 3-section: title / attributes / methods |
| Separator | `line;strokeWidth=1;fillColor=none;align=left;verticalAlign=middle;spacingTop=-1;spacingLeft=3;spacingRight=10;rotatable=0;labelPosition=left;points=[];portConstraint=eastwest;` | Between sections |
| Inheritance | `endArrow=block;endFill=0;` | Hollow triangle arrow |
| Implementation | `endArrow=block;endFill=0;dashed=1;` | Dashed + hollow triangle |
| Composition | `endArrow=diamondThin;endFill=1;` | Filled diamond |
| Aggregation | `endArrow=diamondThin;endFill=0;` | Hollow diamond |
| Dependency | `endArrow=open;dashed=1;` | Dashed + open arrow |
| Layout | TB, classes 250px apart | Interfaces above implementations |

## 9. State Machine Diagram

| Element | Style | Notes |
|---------|-------|-------|
| State | `rounded=1;whiteSpace=wrap;html=1;` | Standard rounded rect |
| Initial state | `ellipse;whiteSpace=wrap;html=1;fillColor=#000000;strokeColor=#000000;` | Small filled circle, ~20x20 |
| Final state | Inner: `ellipse;fillColor=#000000;` + Outer: `ellipse;fillColor=none;strokeColor=#000000;` | Circle-in-circle |
| Choice | `rhombus;whiteSpace=wrap;html=1;` | Small diamond |
| Fork/Join bar | `rounded=0;whiteSpace=wrap;html=1;fillColor=#000000;strokeColor=#000000;` | width=200, height=10 |
| Transition | `edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;` | Label: `event [guard] / action` |
| Layout | TB, initial top-left, final bottom-right | Guard conditions in `[brackets]` |

## 10. Use Case Diagram

| Element | Style | Notes |
|---------|-------|-------|
| Actor | `shape=mxgraph.uml.actor;whiteSpace=wrap;html=1;` | Stick figure |
| Use case | `ellipse;whiteSpace=wrap;html=1;` | Min 140x60 |
| System boundary | `rounded=1;whiteSpace=wrap;html=1;fillColor=none;dashed=1;dashPattern=6 4;` | Dashed rect container |
| Include | `endArrow=open;dashed=1;dashPattern=6 4;` | Label: `<<include>>` |
| Extend | `endArrow=open;dashed=1;dashPattern=6 4;` | Label: `<<extend>>` |
| Layout | System boundary centered, actors outside | Use cases inside |

## 11. Network Topology

| Element | Style | Notes |
|---------|-------|-------|
| Router | `shape=mxgraph.network.wireless_hub;` | See stencils.md for more |
| Switch | `shape=mxgraph.cisco.switch;` | See stencils.md |
| Server | `shape=mxgraph.cisco.server;` | See stencils.md |
| Firewall | `shape=mxgraph.cisco.firewall;` | See stencils.md |
| Cloud | `shape=cloud;whiteSpace=wrap;html=1;` | Built-in cloud shape |
| Subnet/Zone | `rounded=1;whiteSpace=wrap;html=1;fillColor=none;dashed=1;dashPattern=6 4;` | Dashed container |
| Layout | TB: Internet -> Edge -> Core -> Access -> Endpoints | Label with hostname + IP |

## 12. Comparison / Feature Matrix

| Element | Style | Notes |
|---------|-------|-------|
| Header row | `shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=#f3f4f6;fontStyle=1;` | Bold header |
| Data row | `shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;` | Normal row |
| Checkmark cell | `shape=partialRectangle;top=0;left=0;right=0;bottom=1;fillColor=#dcfce7;align=center;` | Green tint + checkmark |
| Empty cell | `shape=partialRectangle;top=0;left=0;right=0;bottom=1;fillColor=#f9fafb;align=center;` | Light gray |
| Layout | Table grid, max 5 columns | Split if more columns needed |

## 13. Timeline / Gantt

| Element | Style | Notes |
|---------|-------|-------|
| Bar | `rounded=1;whiteSpace=wrap;html=1;` + category color | Width = duration |
| Milestone | `rhombus;whiteSpace=wrap;html=1;` | Diamond marker |
| Axis label | `text;html=1;align=center;verticalAlign=middle;resizable=0;points=[];autosize=1;` | Time periods |
| Layout | LR, time on X-axis | Bars horizontally, milestones inline |

## 14. Mind Map / Concept Map

| Element | Style | Notes |
|---------|-------|-------|
| Central node | `ellipse;whiteSpace=wrap;html=1;` or `rounded=1;arcSize=30;` | Large, centered |
| Branch node | `rounded=1;whiteSpace=wrap;html=1;` | Medium |
| Branch edge | `edgeStyle=orthogonalEdgeStyle;rounded=1;curved=1;html=1;` | Curved connections |
| Layout | Radial from center | First-level evenly around, second-level at 30-45 degree offset |

## 15. ML / Deep Learning Model Diagram

| Element | Style | Notes |
|---------|-------|-------|
| Input/Output | `rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;` | Green |
| Conv / Pooling | `rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;` | Blue |
| Attention / Transformer | `rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;` | Purple |
| RNN / LSTM / GRU | `rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;` | Yellow |
| FC / Linear | `rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;` | Orange |
| Loss / Activation | `rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;` | Red/Pink |
| Skip connection | `dashed=1;endArrow=block;curved=1;` | Dashed curved arrow |
| Tensor shape | `value="Conv2D&#xa;(B, 64, 32, 32)"` | Multi-line with `&#xa;` |
| Encoder/Decoder | `swimlane;startSize=24;whiteSpace=wrap;html=1;` | Group as swimlane |
| Layout | TB (data flows top to bottom), layers 150px apart | Annotate tensor dimensions |

## Common Architecture Patterns

These patterns appear frequently. Use them as reference when generating diagrams:

**RAG Pipeline**: Query -> Embed -> VectorSearch -> Retrieve -> Augment -> LLM -> Response

**Agentic RAG**: adds Agent loop with Tool use between Query and LLM

**Agentic Search**: Query -> Planner -> [Search Tool / Calculator / Code] -> Synthesizer -> Response

**Memory Layer**: Input -> Memory Manager -> [Write: VectorDB + GraphDB] / [Read: Retrieve+Rank] -> Context

**Agent Memory Types**: Sensory (raw input) -> Working (context window) -> Episodic (past interactions) -> Semantic (facts) -> Procedural (skills)

**Multi-Agent**: Orchestrator -> [SubAgent A / SubAgent B / SubAgent C] -> Aggregator -> Output

**Tool Call Flow**: LLM -> Tool Selector -> Tool Execution -> Result Parser -> LLM (loop)

**Microservices**: Client -> API Gateway -> [Auth Svc / Product Svc / Order Svc] -> [User DB / Product DB / Redis] -> Message Bus
