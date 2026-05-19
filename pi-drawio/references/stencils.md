# draw.io Built-in Stencil Reference

draw.io includes hundreds of built-in stencils accessible via `shape=mxgraph.*` in the style string. This is a curated list of the most useful ones.

## UML Stencils

| Shape Name | style value | Use for |
|-----------|-------------|---------|
| Actor | `shape=mxgraph.uml.actor;` | Use case actors |
| Lifeline | `shape=umlLifeline;perimeter=lifelinePerimeter;` | Sequence diagram |
| Fragment | `shape=mxgraph.uml.fragment;` | Sequence frames (loop/alt/opt) |
| State | `rounded=1;` (use rounded rect) | State machine |
| Note | `shape=note;whiteSpace=wrap;html=1;` | UML notes |
| Interface | `ellipse;whiteSpace=wrap;html=1;` | Interface circles |

## AWS Stencils

| Shape Name | style value | Use for |
|-----------|-------------|---------|
| Resource Icon | `shape=mxgraph.aws4.resourceIcon;mxgraph.aws4.resourceIcon.icons=TYPE;` | Any AWS service |
| Group | `shape=mxgraph.aws4.group;` | AWS region/group |
| Resource Group | `shape=mxgraph.aws4.resourceGroup;` | Resource grouping |

Common TYPE values: `ec2_instance`, `lambda_function`, `rds_instance`, `s3_bucket`, `api_gateway`, `dynamodb_table`, `sns_topic`, `sqs_queue`, `cloudfront`, `route53`, `vpc`, `subnet`, `security_group`, `iam_role`, `cloudwatch`

## Cisco Network Stencils

| Shape Name | style value | Use for |
|-----------|-------------|---------|
| Router | `shape=mxgraph.cisco.router;` | Network routers |
| Switch | `shape=mxgraph.cisco.switch;` | Network switches |
| Server | `shape=mxgraph.cisco.server;` | Servers |
| Firewall | `shape=mxgraph.cisco.firewall;` | Firewalls |
| Cloud | `shape=mxgraph.cisco.cloud;` | Cloud/Internet |
| Load Balancer | `shape=mxgraph.cisco.load_balancer;` | Load balancers |
| Workstation | `shape=mxgraph.cisco.workstation;` | End-user devices |
| Phone | `shape=mxgraph.cisco.phone;` | VoIP phones |
| Wireless | `shape=mxgraph.cisco.wireless_router;` | WiFi routers |

## Network Stencils (Generic)

| Shape Name | style value | Use for |
|-----------|-------------|---------|
| Wireless Hub | `shape=mxgraph.network.wireless_hub;` | WiFi access points |
| Server Rack | `shape=mxgraph.network.server_rack;` | Rack servers |
| Database | `shape=mxgraph.network.database;` | Network DB |
| Firewall (generic) | `shape=mxgraph.network.firewall;` | Generic firewall |
| Router (generic) | `shape=mxgraph.network.router;` | Generic router |

## Azure Stencils

| Shape Name | style value | Use for |
|-----------|-------------|---------|
| Resource Icon | `shape=mxgraph.azure.resourceIcon;mxgraph.azure.resourceIcon.icons=TYPE;` | Azure services |

Common TYPE values: `app_services`, `functions`, `sql_databases`, `cosmos_db`, `storage_accounts`, `virtual_machines`, `key_vault`, `api_management`, `service_bus`, `event_grid`, `cdn_profiles`, `load_balancers`, `application_gateway`, `azure_ad`, `monitor`, `logic_apps`

## General Shapes

| Shape Name | style value | Use for |
|-----------|-------------|---------|
| Cloud | `shape=cloud;whiteSpace=wrap;html=1;` | Internet/cloud |
| Document | `shape=document;whiteSpace=wrap;html=1;` | Files/reports |
| Note | `shape=note;whiteSpace=wrap;html=1;` | Annotations |
| Card | `shape=card;whiteSpace=wrap;html=1;` | Card-style nodes |
| Callout | `shape=callout;whiteSpace=wrap;html=1;` | Callout annotations |
| Step | `shape=step;perimeter=stepPerimeter;whiteSpace=wrap;html=1;` | Process steps |
| Hexagon | `shape=hexagon;whiteSpace=wrap;html=1;` | Agents, gateways |
| Tape | `shape=tape;whiteSpace=wrap;html=1;` | Curved-top shapes |
| Cube | `shape=cube;whiteSpace=wrap;html=1;` | 3D boxes |
| Cylinder3 | `shape=cylinder3;whiteSpace=wrap;html=1;` | Databases |
| Cylinder | `shape=cylinder;whiteSpace=wrap;html=1;` | Legacy cylinder |
| Folder | `shape=folder;whiteSpace=wrap;html=1;` | File folders |
| Component | `shape=component;align=left;whiteSpace=wrap;html=1;` | UML components |
| Required Interface | `shape=requiredInterface;` | UML interfaces |
| Provided Interface | `shape=providedInterface;` | UML interfaces |
| Parallelogram | `shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;` | I/O in flowcharts |
| Trapezoid | `shape=trapezoid;perimeter=trapezoidPerimeter;whiteSpace=wrap;html=1;` | Manual operations |
| Single Arrow | `shape=singleArrow;whiteSpace=wrap;html=1;` | Arrow-shaped nodes |
| Double Arrow | `shape=doubleArrow;whiteSpace=wrap;html=1;` | Bidirectional |
| Cross | `shape=cross;whiteSpace=wrap;html=1;` | Delete/cancel |
| Wave | `shape=wave;whiteSpace=wrap;html=1;` | Signal/waveform |

## Table Shapes

| Shape Name | style value | Use for |
|-----------|-------------|---------|
| Table | `shape=table;startSize=30;container=1;collapsible=1;childLayout=tableLayout;fixedRows=1;rowLines=0;` | ER tables, matrices |
| Table Row | `shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;` | Table rows |
| Partial Rectangle | `shape=partialRectangle;top=0;left=0;right=0;bottom=1;fillColor=none;align=left;` | Table cells |

## Usage Tips

1. For AWS/Azure stencils, the `icons=` parameter selects the specific service icon
2. Network stencils work best with `fillColor` matching the brand color
3. Always add `whiteSpace=wrap;html=1;` for text rendering
4. Mix stencils with style properties: `shape=mxgraph.cisco.router;fillColor=#f5f5f5;strokeColor=#666666;fontColor=#111827;`
5. When a stencil is unavailable in the installed draw.io version, fall back to `rounded=1;` with semantic coloring
