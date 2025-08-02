version: 0.1.5
Author: Miguel Marina <karel.capek.robotics@gmail.com> - [LinkedIn](https://www.linkedin.com/in/progman32/)
# AutoML

AutoML is an automotive modeling language. It lets you model items, operating scenarios, functions, structure and interfaces. The tool also performs **systems safety analyses**, including cybersecurity, following ISO 26262, ISO 21448, ISO 21434 and ISO 8800 standards. Recent updates add a **Review Toolbox** supporting peer and joint review workflows. The explorer pane now includes an **Analyses** tab organized into *System Design*, *Hazard Analysis*, *Risk Assessment* and *Safety Analysis* sections so documents and diagrams can be opened directly. Architecture objects can now be resized either by editing width and height values or by dragging the red handles that appear when an item is selected. Fork and join bars keep a constant thickness so only their length changes. **Deleting objects on a diagram now asks whether to remove them from the model or only from the current view.** New FMEDA functionality automatically fills the violated safety goal from chosen malfunctions, supports selecting multiple malfunction effects and prevents assigning one malfunction to more than one top level event. Malfunctions can be added or removed via **Add** and **Delete** buttons in the FMEA/FMEDA dialogs, but deletion is blocked for malfunctions currently used in analyses or FTAs.

## Index

- [Workflow Overview](#workflow-overview)
- [HAZOP Analysis](#hazop-analysis)
- [HARA Analysis](#hara-analysis)
- [Requirements Creation and Management](#requirements-creation-and-management)
- [AutoML Diagrams and Safety Analyses](#automl-diagrams-and-safety-analyses)
- [Metamodel Overview](#metamodel-overview)
  - [AutoML Safety Extensions](#automl-safety-extensions)
  - [Core SysML Elements](#core-sysml-elements)
  - [Diagram Relationships](#diagram-relationships)
  - [Detailed Safety and Reliability Metamodel](#detailed-safety-and-reliability-metamodel)
  - [Extended AutoML Element Attributes](#extended-automl-element-attributes)
- [BOM Integration with AutoML Diagrams](#bom-integration-with-automl-diagrams)
- [Component Qualifications](#component-qualifications)
- [Mission Profiles and Probability Formulas](#mission-profiles-and-probability-formulas)
- [SOTIF Analysis](#sotif-analysis)
  - [SOTIF Traceability](#sotif-traceability)
- [Review Toolbox](#review-toolbox)
- [Additional Tools](#additional-tools)
  - [Common Cause Toolbox](#common-cause-toolbox)
  - [Risk & Assurance Gate Calculator](#risk--assurance-gate-calculator)
  - [Safety Goal Export](#safety-goal-export)
- [Email Setup](#email-setup)
- [Dependencies](#dependencies)
- [Diagram Styles](#diagram-styles)
- [License](#license)
- [Building the Executable](#building-the-executable)
- [Version History](#version-history)

## Workflow Overview

The diagram below illustrates how information flows through the major work products. Each box lists the main inputs and outputs so you can see how analyses feed into one another and where the review workflow fits. Approved reviews update the ASIL values propagated throughout the model.

```mermaid
flowchart TD
    subgraph ext [External inputs]
        X([BOM])
    end
    X --> R([Reliability analysis<br/>inputs: BOM<br/>outputs: FIT rates & parts])
    A([System functions & architecture]) --> B([HAZOP<br/>inputs: functions<br/>outputs: malfunctions])
    A --> S([FI2TC / TC2FI<br/>inputs: functions<br/>outputs: hazards, FIs & TCs, severity])
    B --> C([HARA<br/>inputs: malfunctions & SOTIF severity<br/>outputs: hazards, ASIL, safety goals])
    S --> C
    A --> D([FMEA / FMEDA<br/>inputs: architecture, malfunctions, reliability<br/>outputs: failure modes])
    R --> D
    C --> D
    C --> E([FTA<br/>inputs: hazards & safety goals<br/>outputs: fault trees])
    D --> E
    E --> F([Safety requirements<br/>inputs: fault trees & failure modes])
    F --> G([Peer/Joint review<br/>inputs: requirements & analyses<br/>outputs: approved changes])
    G --> H([ASIL propagation to SGs, FMEAs and FTAs])
```

The workflow begins by entering system functions and architecture elements. A **BOM** is imported into a **Reliability analysis** which produces FIT rates and component lists used by the **FMEA/FMEDA** tables. A **HAZOP** analysis identifies malfunctions while the **FI2TC/TC2FI** tables capture SOTIF hazards, functional insufficiencies and triggering conditions along with their severities. The **HARA** inherits these severities and assigns hazards and ASIL ratings to safety goals which then inform FMEDAs and **FTA** diagrams. Fault trees and failure modes generate safety requirements that go through peer or joint **reviews**. When a review is approved any changes to requirements or analyses automatically update the ASIL values traced back to the safety goals, FMEAs and FTAs.

## HAZOP Analysis

The **HAZOP Analysis** window lets you list system functions with one or more associated malfunctions. Each entry records the malfunction guideword (*No/Not*, *Unintended*, *Excessive*, *Insufficient* or *Reverse*), the related scenario, driving conditions and hazard, and whether it is safety relevant. Covered malfunctions may reference other entries as mitigation. When a function is allocated to an active component in a reliability analysis, its malfunctions become selectable failure modes in the FMEDA table.

## HARA Analysis

The **HARA Analysis** view builds on the safety relevant malfunctions from one or more selected HAZOPs. When creating a new HARA you can pick multiple HAZOP documents; only malfunctions from those selections appear in the table. Each HARA table contains the following columns:

1. **Malfunction** – combo box listing malfunctions flagged as safety relevant in the chosen HAZOP documents.
2. **Hazard** – textual description of the resulting hazard.
3. **Severity** – ISO&nbsp;26262 severity level (1–3). Values from FI2TC and
   TC2FI analyses are inherited here so the HARA reflects SOTIF hazards.
4. **Severity Rationale** – free text explanation for the chosen severity.
5. **Controllability** – ISO&nbsp;26262 controllability level (1–3).
6. **Controllability Rationale** – free text explanation for the chosen controllability.
7. **Exposure** – ISO&nbsp;26262 exposure level (1–4).
8. **Exposure Rationale** – free text explanation for the chosen exposure.
9. **ASIL** – automatically calculated from severity, controllability and exposure using the ISO&nbsp;26262 risk graph.
10. **Safety Goal** – combo box listing all defined safety goals in the project.

The calculated ASIL from each row is propagated to the referenced safety goal so that inherited ASIL levels appear consistently in all analyses and documentation, including FTA top level events.

The **Hazard Explorer** window lists all hazards from every HARA in a read-only table for quick review or CSV export. A **Requirements Explorer** window lets you query global requirements with filters for text, type, ASIL and status.

## Requirements Creation and Management

Safety requirements are defined directly on FTA nodes and FMEA entries. In the edit dialog for a node or table row use **Add New** to create a fresh requirement or **Add Existing** to reuse one from the global registry. A new requirement records an ID, type (vehicle, operational, functional safety, technical safety, functional modification or cybersecurity), ASIL, CAL and descriptive text. Requirements can be split into two with the **Decompose** button which assigns ASIL values according to ISO 26262 decomposition rules. All requirements are stored in a project-wide list so they can be attached to multiple elements.

Open the **Requirements Matrix** from the Requirements menu to see every requirement with its allocation to basic events and any traced safety goals. The matrix view links to a **Requirements Editor** where you can add, edit or delete entries and modify traceability. Requirement statuses automatically change from draft to *in review*, *peer reviewed*, *pending approval* and finally *approved* as associated reviews progress. Updating a requirement reopens affected reviews so feedback is always tracked against the latest version.

## AutoML Diagrams and Safety Analyses

Use case, activity, block and internal block diagrams can be created from the **Architecture** menu. Diagrams are stored inside a built-in SysML repository and appear in the *Analyses* explorer under *System Design* so they can be reopened alongside safety documents. Each object keeps its saved size and properties so layouts remain stable when returning to the project.

Activity diagrams list individual **actions** that describe the expected behavior for a block. These actions can be referenced directly in HAZOP tables as potential malfunctions. When a block is linked to a reliability analysis, any actions in its internal block diagram are inherited as additional failure modes for that analysis. The inherited actions automatically show up in new FMEDA tables along with the failure modes already defined for the analysis components.

Elements on a diagram may reference reliability analyses. Choosing an **analysis** or **component** automatically fills the **fit**, **qualification** and **failureModes** fields using data from FMEA and FMEDA tables. These values show up in a *Reliability* compartment for blocks or below parts. When a block references an analysis, the components from that analysis BOM can be inserted as parts in the linked internal block diagram with their failure modes already listed.

Requirements can also be attached to diagram elements to keep architecture and safety analyses synchronized. The same safety goals referenced in HAZOP or HARA tables can therefore be traced directly to the blocks and parts that implement them.

## Metamodel Overview

Internally, AutoML stores all model elements inside a lightweight SysML repository. Each element is saved with its specific type—`BlockUsage`, `PartUsage`, `PortUsage`, `ActivityUsage`, `ActionUsage`, `UseCase`, `Actor` and so on. Links between these typed elements use the `SysMLRelationship` class. Diagrams such as use case or block diagrams are stored as `SysMLDiagram` objects containing the drawn **objects** and their **connections**. The singleton `SysMLRepository` manages every element, relationship and diagram so analyses stay consistent across the application. Each element ID is listed in an `element_diagrams` mapping so name or property updates propagate to every diagram where that element appears.

```mermaid
classDiagram
    class SysMLRepository {
        elements: Dict~str, SysMLElement~
        relationships: List~SysMLRelationship~
        diagrams: Dict~str, SysMLDiagram~
        element_diagrams: Dict~str, str~
        +create_element()
        +create_relationship()
        +create_diagram()
    }
    class SysMLElement {
        elem_id: str
        elem_type: str
        name: str
        properties: Dict~str, str~
        stereotypes: Dict~str, str~
        owner: str
    }
    class SysMLRelationship {
        rel_id: str
        rel_type: str
        source: str
        target: str
        stereotype: str
        properties: Dict~str, str~
    }
    class SysMLDiagram {
        diag_id: str
        diag_type: str
        name: str
        package: str
        description: str
        color: str
        elements: List~str~
        relationships: List~str~
        objects: List~SysMLObject~
        connections: List~DiagramConnection~
    }
    class SysMLObject {
        obj_id: int
        obj_type: str
        x: float
        y: float
        element_id: str
        width: float
        height: float
        properties: Dict~str, str~
        requirements: List~dict~
        locked: bool
        hidden: bool
    }
    class DiagramConnection {
        src: int
        dst: int
        conn_type: str
        style: str
        points: List~Tuple~float,float~~
        src_pos: Tuple~float,float~~
        dst_pos: Tuple~float,float~~
        name: str
        arrow: str
        mid_arrow: bool
        multiplicity: str
    }
    class BlockUsage
    class PartUsage
    class PortUsage
    class ActivityUsage
    class ActionUsage
    class SafetyGoal
    class Hazard
    class Scenario
    class FaultTreeNode
    SysMLRepository --> "*" BlockUsage
    SysMLRepository --> "*" PartUsage
    SysMLRepository --> "*" PortUsage
    SysMLRepository --> "*" ActivityUsage
    SysMLRepository --> "*" ActionUsage
    SysMLRepository --> "*" SafetyGoal
    SysMLRepository --> "*" Hazard
    SysMLRepository --> "*" Scenario
    SysMLRepository --> "*" FaultTreeNode
    SysMLRepository --> "*" SysMLRelationship
    SysMLRepository --> "*" SysMLDiagram
    SysMLDiagram --> "*" SysMLObject
    SysMLDiagram --> "*" DiagramConnection
    SysMLObject --> "0..1" BlockUsage
    SysMLObject --> "0..1" PartUsage
    SysMLObject --> "0..1" PortUsage
    SysMLObject --> "0..1" ActivityUsage
    SysMLObject --> "0..1" ActionUsage
    SysMLObject --> "0..1" SafetyGoal
    SysMLObject --> "0..1" Hazard
    SysMLObject --> "0..1" Scenario
    SysMLObject --> "0..1" FaultTreeNode
```

### AutoML Safety Extensions

AutoML builds on this base by introducing domain specific stereotypes for safety
analysis. Hazards, faults and scenarios are stored using explicit types such as
`Hazard`, `Scenario`, `Scenery`, `SafetyGoal` and `FaultTreeNode`. Tables like
HAZOP or HARA reference these elements so analyses remain linked to the
architecture.

```mermaid
classDiagram
    class SafetyGoal
    class Hazard
    class Scenario
    class Scenery
    class FaultTreeNode
    class Fault
    class Failure
    class FmedaDoc
    class FmeaDoc
    class FaultTreeDiagram
    class TriggeringCondition
    class FunctionalInsufficiency
    class FunctionalModification
    class AcceptanceCriteria
    SafetyGoal --> "*" Hazard : mitigates
    Scenario --> "*" Hazard : leadsTo
    Scenario --> Scenery : occursIn
    Scenario --> TriggeringCondition : has
    Scenario --> FunctionalInsufficiency : reveals
    TriggeringCondition --> FunctionalInsufficiency : leadsTo
    FunctionalInsufficiency --> FunctionalModification : mitigatedBy
    FunctionalModification --> AcceptanceCriteria : verifiedBy
    Fault --> Failure : leadsTo
    FmeaDoc --> Fault : records
    FmeaDoc --> Failure : records
    FaultTreeNode --> Failure : baseEvent
    FaultTreeNode --> "*" SafetyGoal : traces
    FaultTreeDiagram --> "*" FaultTreeNode : contains
    FaultTreeDiagram --> FmeaDoc : uses
    FaultTreeDiagram --> FmedaDoc : uses
```

### Core SysML Elements

The repository tracks each element by its specific type rather than using the
generic `SysMLElement` placeholder. Key classes include:

- **BlockUsage** – structural block definition. Properties: `partProperties`,
  `ports`, `operations`, plus reliability attributes `analysis`, `fit`,
  `qualification` and `failureModes`.
- **PartUsage** – internal part with `component`, `failureModes` and `asil`
  fields for BOM links and safety ratings.
  Parts created automatically for composite aggregations set a `force_ibd`
  property so an internal block diagram is generated when the block structure is
  first opened.
- **PortUsage** – port on a block or part. Provides `direction`, `flow`,
  `labelX` and `labelY` to specify connector orientation.
- **ActivityUsage** – container for behaviors with `ownedActions` and
  `parameters`.
- **ActionUsage** – atomic step within an activity. Can be specialized as
  `CallBehaviorAction` to invoke another activity.
- **ControlFlow** and **ObjectFlow** – edges between actions. Control flows
  handle sequencing while object flows carry typed data.
- **Use Case** and **Actor** – high level functional views capturing external
  interactions.

```mermaid
classDiagram
    class BlockUsage
    class PartUsage
    class PortUsage
    class ActivityUsage
    class ActionUsage
    class ControlFlow
    class ObjectFlow
    class UseCase
    class Actor
    BlockUsage "1" o-- "*" PartUsage : parts
    BlockUsage --> "*" PortUsage : ports
    BlockUsage --> "*" ActivityUsage : behaviors
    PartUsage --> "*" PortUsage : ports
    ActivityUsage --> "*" ActionUsage : actions
    ActionUsage --> "*" ControlFlow : control
    ActionUsage --> "*" ObjectFlow : objects
    UseCase --> "*" Actor : actors
    UseCase --> ActivityUsage : realizedBy
```

### Diagram Relationships

Internal block diagrams provide structural views of a block. The diagram displays the block's parts and their ports so connectors can be drawn between them. Actions in activity diagrams may also reference an internal block diagram that explains the hardware interaction for that step.

```mermaid
classDiagram
    class BlockUsage
    class PartUsage
    class PortUsage
    class SysMLDiagram
    class InternalBlockDiagram
    class ActionUsage
    SysMLDiagram <|-- InternalBlockDiagram
    BlockUsage --> InternalBlockDiagram : structureView
    InternalBlockDiagram --> "*" PartUsage : shows
    InternalBlockDiagram --> "*" PortUsage : ports
    PartUsage --> "*" PortUsage : ports
    ActionUsage --> InternalBlockDiagram : view
```

### Detailed Safety and Reliability Metamodel

The tool stores each safety analysis in its own container object alongside the
SysML repository. These containers track the tables and diagrams loaded in the
GUI so analyses remain linked to the architecture. Key data classes include:

```mermaid
classDiagram
    SysMLRepository --> "*" ReliabilityAnalysis
    ReliabilityAnalysis --> "*" ReliabilityComponent
    SysMLRepository --> "*" HazopDoc
    HazopDoc --> "*" HazopEntry
    SysMLRepository --> "*" HaraDoc
    HaraDoc --> "*" HaraEntry
    SysMLRepository --> "*" FmeaDoc
    FmeaDoc --> "*" FmeaEntry
    SysMLRepository --> "*" FmedaDoc
    FmedaDoc --> "*" FmeaEntry
    FmeaEntry --> Fault : cause
    FmeaEntry --> Failure : effect
    Failure --> FaultTreeNode : representedBy
    SysMLRepository --> "*" FI2TCDoc
    SysMLRepository --> "*" TC2FIDoc
    FI2TCDoc --> "*" FI2TCEntry
    TC2FIDoc --> "*" TC2FIEntry
    FI2TCEntry --> FunctionalInsufficiency
    FI2TCEntry --> TriggeringCondition
    FI2TCEntry --> Scenario
    FI2TCEntry --> Hazard : hazard
    FI2TCEntry --> HaraEntry : severity
    TC2FIEntry --> TriggeringCondition
    TC2FIEntry --> FunctionalInsufficiency
    TC2FIEntry --> Hazard : hazard
    TC2FIEntry --> HaraEntry : severity
    SysMLRepository --> "*" Hazard
    SysMLRepository --> "*" FunctionalModification
    FunctionalModification --> "*" AcceptanceCriteria
    SysMLRepository --> "*" AcceptanceCriteria
    SysMLRepository --> "*" TriggeringCondition
    SysMLRepository --> "*" FunctionalInsufficiency
    SysMLRepository --> "*" Fault
    SysMLRepository --> "*" Failure
    class FI2TCEntry
    class TC2FIEntry
    class Hazard
    class HaraEntry
    class TriggeringCondition
    class FunctionalInsufficiency
    class FunctionalModification
    class AcceptanceCriteria
    class FaultTreeNode
    class Fault
    class Failure
```

`ReliabilityAnalysis` records the selected standard, mission profile and overall
FIT results. Each `ReliabilityComponent` lists attributes like qualification,
quantity and a dictionary of part‑specific parameters. HAZOP and HARA tables use
`HazopDoc`/`HazopEntry` and `HaraDoc`/`HaraEntry` pairs to store their rows. FMEA
and FMEDA tables are stored as `FmeaDoc` and `FmedaDoc` with lists of generic
`FmeaEntry` dictionaries capturing the failure mode, cause, detection rating and
diagnostic coverage. Fault tree diagrams consist of nested `FaultTreeNode`
objects that hold FMEA metrics, FMEDA values and traced requirements.

#### Analysis Relationships

The diagram below shows how reliability calculations flow into FMEDA tables and fault trees.

```mermaid
classDiagram
    class BlockUsage
    class PartUsage
    class HazopEntry
    class FmeaDoc
    class FaultTreeDiagram
    class Fault
    class Failure
    class FmeaEntry
    class FmedaDoc
    class ReliabilityAnalysis
    class ReliabilityComponent
    BlockUsage --> ReliabilityAnalysis : analysis
    ReliabilityAnalysis --> "*" ReliabilityComponent : components
    PartUsage --> ReliabilityComponent : component
    HazopEntry --> FmeaEntry : failureMode
    FmeaDoc --> "*" FmeaEntry : rows
    FmeaEntry --> Fault : cause
    FmeaEntry --> Failure : effect
    Failure --> FaultTreeNode : event
    FmedaDoc --> "*" FmeaEntry : rows
    PartUsage --> "*" FmeaEntry : failureModes
    ReliabilityComponent --> "*" FmeaEntry : modes
    FmeaEntry --> FaultTreeNode : baseEvent
    SysMLDiagram <|-- FaultTreeDiagram
    FaultTreeDiagram --> "*" FaultTreeNode : nodes
```

Blocks reference a `ReliabilityAnalysis` which lists its components. Parts link directly to the matching `ReliabilityComponent`. Malfunctions selected from `HazopEntry` rows become `FmeaEntry` failure modes tied to those components. The base FIT for each `ReliabilityComponent` feeds into FMEDA tables so a separate FIT is calculated for every failure mode. These FMEDA entries can spawn `FaultTreeNode` base events inside an FTA diagram so probabilities and coverage remain synchronized with the reliability analysis.

#### Hazard Traceability

The next diagram traces how malfunctions detected in a HAZOP flow through the safety analyses. Actions in activity diagrams become `HazopEntry` malfunctions linked to operational `Scenario` objects and their `Scenery` from the ODD. Selected HAZOP rows populate `HaraEntry` items where Severity × Exposure × Controllability determine the ASIL and resulting `SafetyGoal`. Safety goals appear as the top level events in FTAs. FMEDA failure modes and architecture components create `FaultTreeNode` base events that generate safety `Requirement` objects. Requirements may be decomposed into children with reduced ASIL values when ISO 26262 decomposition rules apply.

```mermaid
classDiagram
    class UseCase
    class ActivityUsage
    class ActionUsage
    class HazopEntry
    class Scenario
    class Scenery
    class HaraEntry
    class Hazard
    class SafetyGoal
    class FmeaEntry
    class FaultTreeDiagram
    class FaultTreeNode
    class Fault
    class Failure
    class Requirement
    UseCase --> ActivityUsage : realizedBy
    ActivityUsage --> "*" ActionUsage : actions
    ActivityUsage --> HazopEntry : hazopInput
    ActionUsage --> HazopEntry : malfunction
    Scenario --> HazopEntry : analyzedIn
    Scenery --> Scenario : contextFor
    HazopEntry --> HaraEntry : selected
    HazopEntry --> Fault : fault
    Fault --> Failure : resultsIn
    FmeaEntry --> Fault : cause
    FmeaEntry --> Failure : effect
    Failure --> FaultTreeNode : event
    HaraEntry --> Hazard
    HaraEntry --> SafetyGoal
    SafetyGoal --> FaultTreeDiagram : topEvent
    FmeaEntry --> FaultTreeNode : baseEvent
    FaultTreeDiagram --> "*" FaultTreeNode : nodes
    FaultTreeNode --> Requirement : requirement
    Requirement --> "0..*" Requirement : decomposedInto
```

#### Differences From Standard SysML

- **BlockUsage** – extends the standard `Block` with reliability information:
  `analysis`, `fit`, `qualification` and `failureModes` link architecture
  elements to FMEA tables.
- **PartUsage** – extends `PartProperty` by referencing a BOM `component`,
  listing applicable `failureModes` and storing the assigned `asil` level.
- **SafetyGoal** – specialization of `Requirement` holding a textual
  `description`, `asil` rating and quantitative targets `spfm`, `lpfm` and `dc`.
- **Hazard** – extends `SysMLElement` with a hazard `description` and HARA
  `severity` plus the related `scenarios`.
- **Scenario** – extends `SysMLElement` to include a short `description`, linked
  `scenery` context and traced `hazards`.
- **Scenery** – extends `SysMLElement` with the `odd_element` name and flexible
  context `attributes` describing that environment.
- **FaultTreeNode** – extends `SysMLElement` by storing FMEA fields
  `fmea_effect` and `fmea_cause`, FMEDA metrics and traced
  `safety_requirements`.
- **ReliabilityAnalysis** – specialization of `AnalysisDocument` capturing the
  selected reliability `standard`, mission `profile`, aggregated `total_fit` and
  resulting `spfm`, `lpfm` and `dc` values.
- **ReliabilityComponent** – extends `SysMLElement` with component `name`,
  qualification certificate, `quantity`, parameter `attributes` and computed
  `fit` rate.
- **FmeaDoc** – specialized `AnalysisDocument` holding the failure mode table
  with occurrence and detection ratings.
- **FmeaEntry** – extends `SysMLElement` with `failure_mode`, `cause`, `effect`,
  `severity`, `occurrence` and `detection` data.
- **FmedaDoc** – specialized `AnalysisDocument` whose table-level metrics
  `spfm`, `lpfm` and `dc` are calculated from failure mode FIT values.
- **FaultTreeDiagram** – specialization of `SysMLDiagram` storing the overall
  fault tree probability `phmf` and Prototype Assurance Level `pal`.
- **TriggeringCondition** – extends `SysMLElement` with a textual
  `description`, the related `scenario` and any allocated acceptance criteria.
- **FunctionalInsufficiency** – extends `SysMLElement` with the missing function
  `description`, associated `scenario` and impacted `safetyGoal`.
- **FunctionalModification** – extends `SysMLElement` to record the mitigation
  text and linked `acceptanceCriteria` used to verify the change.
- **AcceptanceCriteria** – extends `SysMLElement` with a measurable condition
  proving a functional modification resolves the hazard.
- **Fault** – extends `SysMLElement` to describe the underlying cause leading to
  a failure mode.
- **Failure** – extends `SysMLElement` to record the malfunction effect used as
  an FMEA failure mode and FTA event.

### Extended AutoML Element Attributes

AutoML elements include additional properties beyond the standard SysML fields.
Key attributes are:

- **SafetyGoal** – textual `description`, assigned `asil` level and quantitative
  targets `spfm`, `lpfm` and `dc`. Each goal also lists allocated safety
  `requirements`.
- **Hazard** – hazard `description`, HARA `severity` and the related
  `scenarios` that can lead to it.
- **Scenario** – short `description`, linked `scenery` context and traced
  `hazards`.
- **Scenery** – stores the `odd_element` name and an open-ended set of
  context attributes describing that element.
- **FaultTreeNode** – FMEA fields `fmea_effect` and `fmea_cause`, FMEDA metrics
  `fmeda_fit`, `fmeda_diag_cov`, `fmeda_spfm`, `fmeda_lpfm`, the calculated
  `failure_prob` and a list of `safety_requirements`.
- **ReliabilityAnalysis** – selected `standard`, mission `profile`, aggregated
  `total_fit` and resulting `spfm`, `lpfm` and `dc` values.
- **ReliabilityComponent** – component `name`, qualification certificate,
  `quantity`, parameter `attributes` and computed `fit` rate.
- **FmeaDoc** – failure mode table with occurrence and detection ratings.
- **FmedaDoc** – table-level metrics `spfm`, `lpfm` and `dc` calculated from
  failure mode FIT values.
- **FaultTreeDiagram** – overall fault tree probability `phmf` and Prototype
  Assurance Level `pal`.
- **TriggeringCondition** – `description`, related `scenario` and any allocated
  acceptance criteria.
- **FunctionalInsufficiency** – description of the missing function,
  associated `scenario` and the impacted `safetyGoal`.
- **FunctionalModification** – mitigation text and link to one or more
  `acceptanceCriteria` used to verify the change.
- **AcceptanceCriteria** – measurable condition proving a functional
  modification resolves the hazard.
- **Fault** - underlying cause leading to a failure mode.
- **Failure** - malfunction effect used as an FMEA failure mode and FTA event.
- **SysMLObject** – drawn object with coordinates, size and an optional linked
  element. The `locked` flag prevents editing while `hidden` temporarily removes
  the object from the diagram.
- **DiagramConnection** – connector between objects storing the connection
  `style`, optional arrowheads, intermediate points and a `mid_arrow` toggle for
  aggregation lines.

**BlockUsage** – extends `Block` with reliability fields like `analysis`, `fit`, `qualification` and `failureModes`.

```mermaid
classDiagram
    class BlockUsage {
        analysis
        fit
        qualification
        failureModes
    }
    Block <|-- BlockUsage
```

**PartUsage** – extends `PartProperty` with `component`, `failureModes` and `asil` fields.

```mermaid
classDiagram
    class PartUsage {
        component
        failureModes
        asil
    }
    PartProperty <|-- PartUsage
```

**SafetyGoal** – specialization of `Requirement` with `asil` and FMEDA metrics (`spfm`, `lpfm`, `dc`).

```mermaid
classDiagram
    class SafetyGoal {
        asil
        spfm
        lpfm
        dc
    }
    Requirement <|-- SafetyGoal
```

**Hazard** – extends `SysMLElement` to store the hazard `description` and HARA `severity`.

```mermaid
classDiagram
    class Hazard {
        description
        severity
    }
    SysMLElement <|-- Hazard
```

**Scenario** – extends `SysMLElement` with a short `description` and linked `scenery`.

```mermaid
classDiagram
    class Scenario {
        description
        scenery
    }
    SysMLElement <|-- Scenario
```

**Scenery** – extends `SysMLElement` with an `odd_element` name and descriptive `attributes`.

```mermaid
classDiagram
    class Scenery {
        odd_element
        attributes
    }
    SysMLElement <|-- Scenery
```

**FaultTreeNode** – specialized `SysMLElement` capturing FMEA and FMEDA data for FTA events.

```mermaid
classDiagram
    class FaultTreeNode {
        fmea_effect
        fmea_cause
        fmeda_fit
        fmeda_diag_cov
        fmeda_spfm
        fmeda_lpfm
        failure_prob
        safety_requirements
    }
    SysMLElement <|-- FaultTreeNode
```

**ReliabilityAnalysis** – extends `AnalysisDocument` to store mission profile and cumulative FIT metrics.

```mermaid
classDiagram
    class ReliabilityAnalysis {
        standard
        profile
        total_fit
        spfm
        lpfm
        dc
    }
    AnalysisDocument <|-- ReliabilityAnalysis
```
**ReliabilityComponent** – extends `SysMLElement` with component data like `name`, `qualification`, `quantity`, `attributes` and `fit`.


```mermaid
classDiagram
    class ReliabilityComponent {
        name
        qualification
        quantity
        attributes
        fit
    }
    SysMLElement <|-- ReliabilityComponent
```
**AnalysisDocument** – base class for safety tables with `name`, `date` and `description`.


```mermaid
classDiagram
    class AnalysisDocument {
        name
        date
        description
    }
    SysMLElement <|-- AnalysisDocument
```

**FmeaDoc** – extends `AnalysisDocument` for FMEA tables with an `rpn_threshold`.

```mermaid
classDiagram
    class FmeaDoc {
        rpn_threshold
    }
    AnalysisDocument <|-- FmeaDoc
```

**FmeaEntry** – extends `SysMLElement` with failure mode data including `cause`, `effect`, `severity`, `occurrence` and `detection`.

```mermaid
classDiagram
    class FmeaEntry {
        failure_mode
        cause
        effect
        severity
        occurrence
        detection
    }
    SysMLElement <|-- FmeaEntry
```

**FmedaDoc** – another `AnalysisDocument` variant storing table-level `spfm`, `lpfm` and `dc` metrics.

```mermaid
classDiagram
    class FmedaDoc {
        spfm
        lpfm
        dc
    }
    AnalysisDocument <|-- FmedaDoc
```
**FaultTreeDiagram** – specialization of `SysMLDiagram` storing overall probability `phmf` and Prototype Assurance Level `pal`.


```mermaid
classDiagram
    class FaultTreeDiagram {
        phmf
        pal
    }
    SysMLDiagram <|-- FaultTreeDiagram
```

**TriggeringCondition** – extends `SysMLElement` with a `description`, linked `scenario` and associated acceptance criteria.

```mermaid
classDiagram
    class TriggeringCondition {
        description
        scenario
        acceptanceCriteria
    }
    SysMLElement <|-- TriggeringCondition
```

**FunctionalInsufficiency** – extends `SysMLElement` with a failure `description`, linked `scenario` and impacted `safetyGoal`.

```mermaid
classDiagram
    class FunctionalInsufficiency {
        description
        scenario
        safetyGoal
    }
    SysMLElement <|-- FunctionalInsufficiency
```

**FunctionalModification** – extends `SysMLElement` with mitigation `text` and linked acceptance criteria.

```mermaid
classDiagram
    class FunctionalModification {
        text
        acceptanceCriteria
    }
    SysMLElement <|-- FunctionalModification
```
**AcceptanceCriteria** – extends `SysMLElement` with a textual description verifying a functional modification.


```mermaid
classDiagram
    class AcceptanceCriteria {
        description
    }
    SysMLElement <|-- AcceptanceCriteria
```
**Fault** – extends `SysMLElement` to describe an underlying cause leading to a failure mode.

```mermaid
classDiagram
    class Fault {
        description
    }
    SysMLElement <|-- Fault
```

**Failure** – extends `SysMLElement` to capture a malfunction effect and its `severity`.

```mermaid
classDiagram
    class Failure {
        description
        severity
    }
    SysMLElement <|-- Failure
```

## BOM Integration with AutoML Diagrams

Blocks in block diagrams may reference saved reliability analyses via the **analysis** property while parts reference individual components using the **component** property. Both element types also provide **fit**, **qualification** and **failureModes** attributes. Entering values for these fields shows them in a *Reliability* compartment for blocks or as additional lines beneath parts so FIT rates and qualification information remain visible in the AutoML model. When editing a block or part you can now pick from drop-down lists containing all analyses or components from saved reliability analyses. Selecting an item automatically fills in its FIT rate, qualification certificate and any failure modes found in FMEA tables.

## Component Qualifications

Reliability calculations take the qualification certificate of each passive component into account. When computing FIT rates, a multiplier based on the certificate (e.g. *AEC‑Q200* or *MIL‑STD‑883*) is applied so qualified parts yield lower failure rates. Active components currently use a neutral factor. Additional datasheet parameters such as diode forward voltage or MOSFET `RDS(on)` can be entered when configuring components to better document the parts used in the analysis.

## Mission Profiles and Probability Formulas

The **Reliability** menu lets you define mission profiles describing the on/off time, temperatures and other conditions for your system. When a profile is present its total `TAU` value is used to convert FIT rates into failure probabilities for each basic event.

In the *Edit Node* dialog for a basic event you can choose how the FIT rate is interpreted:

* **linear** – probability is calculated as `λ × τ` where `λ` is the FIT value expressed as failures per hour and `τ` comes from the selected mission profile.
* **exponential** – uses the exponential model `1 − exp(−λ × τ)`.
* **constant** – probability comes from the basic event's *Failure Probability* field and does not use the FIT rate or mission time.

Mission profiles and the selected formula for each basic event are stored in the JSON model so results remain consistent when reloading the file.

## SOTIF Analysis

The **Qualitative Analysis** menu also provides dedicated SOTIF tools. Selecting **Triggering Conditions** or **Functional Insufficiencies** opens read-only lists of each node type with an **Export CSV** button. These views gather all triggering condition and functional insufficiency nodes from the FTAs so the information can be reviewed separately.

Two additional tables support tracing between these elements:

* **FI2TC Analysis** – analogue of HAZOP for SOTIF. Each row links a functional
  insufficiency to the triggering conditions, scenarios and mitigation measures
  that reveal the hazard. The hazard and its **severity** are recorded here. The
  table includes dedicated **triggering_conditions** and
  **functional_insufficiencies** columns populated via comboboxes so new items
  can be added on the fly. The **design_measures** column now shows a list of
  allocated functional modification requirements with **Add New** and
  **Add Existing** buttons just like FTA nodes. Selected requirements appear in
  the listbox and can be edited or removed individually.
* **TC2FI Analysis** – also mirrors HAZOP concepts for SOTIF. It starts from the
  triggering condition and lists the impacted functions, architecture elements
  and related insufficiencies. The identified hazard and its **severity** are
  noted in each entry. The **triggering_conditions** and
  **functional_insufficiencies** fields mirror those in the FI2TC table to keep
  the relationships consistent.

Severity recorded in FI2TC and TC2FI entries is inherited by the HARA so the risk graph reflects the SOTIF findings. Other HARA values such as the associated safety goal flow into these tables so SOTIF considerations remain connected to the overall risk assessment. Minimal cut sets calculated from the FTAs highlight combinations of FIs and TCs that form *CTAs*. From a CTA entry you can generate a functional modification requirement describing how the design must change to avoid the unsafe behaviour.

All FI2TC and TC2FI documents appear in the *Hazard Analysis* section of the **Analyses** tab so they can be opened alongside HARA tables, FTAs and CTAs for a complete view of functional safety and SOTIF issues.

### SOTIF Traceability

The following diagram shows how triggering conditions, functional insufficiencies and functional modifications connect scenarios to safety goals and fault trees. FI2TC and TC2FI tables cross‑reference these elements and record the acceptance criteria for each mitigation.

```mermaid
classDiagram
    class Scenario
    class SafetyGoal
    class TriggeringCondition
    class FunctionalInsufficiency
    class FI2TCDoc
    class TC2FIDoc
    class Hazard
    class HaraEntry
    class FunctionalModification
    class AcceptanceCriteria
    class FaultTreeDiagram
    class FaultTreeNode
    Scenario --> TriggeringCondition : triggers
    Scenario --> FunctionalInsufficiency : reveals
    TriggeringCondition --> FI2TCDoc : entry
    FunctionalInsufficiency --> FI2TCDoc : entry
    TriggeringCondition --> TC2FIDoc : entry
    FunctionalInsufficiency --> TC2FIDoc : entry
    FunctionalInsufficiency --> FunctionalModification : mitigatedBy
    FunctionalModification --> AcceptanceCriteria : validatedBy
    FI2TCDoc --> Hazard : hazard
    TC2FIDoc --> Hazard : hazard
    FI2TCDoc --> HaraEntry : severity
    TC2FIDoc --> HaraEntry : severity
    SafetyGoal --> FaultTreeDiagram : topEvent
    FaultTreeDiagram --> "*" FaultTreeNode : nodes
    TriggeringCondition --> FaultTreeNode : cta
    FunctionalInsufficiency --> FaultTreeNode : cta
```

## Review Toolbox

Launch the review features from the **Review** menu:

* **Start Peer Review** – create at least one moderator and one reviewer, then tick the checkboxes for the FTAs and FMEAs you want to include. Each moderator and participant has an associated email address. A due date is requested and once reached the review becomes read‑only unless a moderator extends it. A document window opens showing the selected elements. FTAs are drawn on canvases you can drag and scroll, while FMEAs appear as full tables listing every field so failures can be reviewed line by line. Linked requirements are listed below and any text changes are colored the same way as other differences. Changes to which requirements are allocated to each item are highlighted in blue and red.
* **Start Joint Review** – add participants with reviewer or approver roles and at least one moderator, select the desired FTAs and FMEAs via checkboxes and enter a unique review name and description. Approvers can approve only after all reviewers are done and comments resolved. Moderators may edit the description, due date or participant list later from the toolbox. The document window behaves the same as for peer reviews with draggable FTAs and tabulated FMEAs. Requirement diffs are also shown in this view.
* Closing a joint review asks for a baseline name which is combined with the automatically incremented version, for example "v4 - baseline_00_98_23". This label appears in the **Compare Versions** dialog.
* **Open Review Toolbox** – manage comments. Selecting a comment focuses the related element and shows the text below the list. Use the **Open Document** button to reopen the visualization for the currently selected review. A drop-down at the top lists every saved review with its approval status.
* **Merge Review Comments** – combine feedback from another saved model into the current one so parallel reviews can be consolidated.
* **Compare Versions** – view earlier approved versions. Differences are listed with a short description and small before/after images of changed FTA nodes. Requirement allocations are compared in the diagrams and logs.
* **Set Current User** – choose who you are when adding comments. The toolbox also provides a drop-down selector.
* **Update Decomposition** – after splitting a requirement into two, select either child and use the new button in the node dialog to pick a different ASIL pair.
* The target selector within the toolbox only lists nodes and FMEA items that were chosen when the review was created, so comments can only be attached to the scoped elements.

Nodes with unresolved comments show a small yellow circle to help locate feedback quickly. When a review document is opened it automatically compares the current model to the previous approved version. Added elements appear in blue and removed ones in red just like the **Compare Versions** tool, but only for the FTAs and FMEAs included in that review.

When comparing versions, added nodes and connections are drawn in blue while removed ones are drawn in red. Text differences highlight deleted portions in red and new text in blue so changes to descriptions, rationales or FMEA fields stand out. Deleted links between FTA nodes are shown with red connectors. Requirement lists are compared as well so allocation changes show up alongside description and rationale edits. The Requirements Matrix window now lists every requirement with the nodes and FMEA items where it is allocated and the safety goals traced to each one.

Comments can be attached to FMEA entries and individual requirements. Resolving a comment prompts for a short explanation which is shown with the original text.

Review information (participants, comments, review names, descriptions and approval state) is saved as part of the model file and restored on load.

## Additional Tools

### Common Cause Toolbox

The **Common Cause Toolbox** groups failures that share the same cause across FMEAs, FMEDAs and FTAs. It highlights events that may lead to common cause failures and supports exporting the aggregated list to CSV.

### Risk & Assurance Gate Calculator

A built-in calculator derives a Prototype Assurance Level (PAL) from confidence, robustness and direct assurance inputs. Gates aggregate assurance from child nodes to help judge whether additional testing or design changes are needed before road trials.

### Safety Goal Export

Use **Export SG Requirements** in the Requirements menu to generate a CSV listing each safety goal with its associated requirements and ASIL ratings.

## Email Setup

When sending review summaries, the application asks for SMTP settings and login details. If you use Gmail with two-factor authentication enabled, create an **app password** and enter it instead of your normal account password. Authentication failures will prompt you to re-enter these settings.

Each summary email embeds PNG images showing the differences between the current model and the last approved version for the selected FTAs so reviewers can view the diagrams directly in the message. CSV files containing the FMEA tables are attached so they can be opened in Excel or another spreadsheet application. Requirement changes with allocations and safety goal traces are listed below the diagrams.

If sending fails with a connection error, the dialog will prompt again so you can correct the server address or port.

## Dependencies

AutoML relies on a few third‑party Python packages which must be installed
before running the tool or creating the executable. Install them with pip:

```
pip install pillow openpyxl networkx matplotlib reportlab adjustText
```

PyInstaller requires these packages to be present so they are bundled into
`AutoML.exe`. Missing dependencies, such as Pillow, will otherwise lead to
`ModuleNotFoundError` when launching the built executable.

Note that Pillow provides the `PIL` module. The build scripts now verify
dependencies with `python -m pip show` so the correct interpreter is used and
pass `--hidden-import=PIL.ImageTk` to PyInstaller to ensure the module is
bundled correctly.

If double‑clicking `AutoML.py` closes immediately, launch it from a command
prompt instead so any error messages remain visible.

## Diagram Styles

Several XML files in the `styles` directory control the colors used for
diagram elements. The default style `pastel.xml` provides softer tones like
peach actions and steel-blue nodes. `modern.xml` offers a Material-inspired
palette for a different look. Open the Style Editor via **View → Style Editor**, click **Load** and choose
the desired style. All open diagrams update immediately.

## License

This project is licensed under the GNU General Public License version 3. See the [LICENSE](LICENSE) file for details.

## Building the Executable
To create a standalone Windows executable with PyInstaller:

- **Linux/macOS:** run `bin/build_exe.sh`
- **Windows:** run `bin\build_exe.bat`

You can invoke these scripts from any directory; they locate the repository
root automatically. Both generate `AutoML.exe` inside the `bin` directory.
After building you can launch the application directly or use
`bin/run_automl.sh` on Unix-like systems or `bin\run_automl.bat` on
Windows.

If a previous build failed and left an `AutoML.spec` file behind, the build
scripts now delete it before running PyInstaller so your command line
options are always applied.

The scripts exclude the `scipy` package, which is not required by AutoML but
can cause PyInstaller to fail on some Python installations. If you encounter
errors about ``IndexError`` while building, try upgrading your Python runtime
or reinstalling SciPy. This is most common when using a pre-release Python
interpreter (e.g. ``3.10.0rc2``). Install the latest stable release of Python
and run the build again if you hit this issue.


## Version History
- 0.1.5 - Added a pastel style with peach actions and steel-blue nodes.
- 0.1.4 - Initial diagram style support documented.
- 0.1.3 - Added context menu actions to remove parts from a diagram or from the model.
- 0.1.2 - Clarified systems safety focus in description and About dialog.
- 0.1.1 - Updated description and About dialog.
- 0.1.0 - Added Help menu and version tracking.
