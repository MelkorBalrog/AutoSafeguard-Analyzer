version: 0.1.2
Author: Miguel Marina <karel.capek.robotics@gmail.com> - [LinkedIn](https://www.linkedin.com/in/progman32/)
# AutoML

AutoML is an automotive modeling language. It lets you model items, operating scenarios, functions, structure and interfaces. The tool also performs **systems safety analyses**, including cybersecurity, following ISO 26262, ISO 21448, ISO 21434 and ISO 8800 standards. Recent updates add a **Review Toolbox** supporting peer and joint review workflows. The explorer pane now includes an **Analyses** tab listing all FMEAs, FMEDAs, HAZOPs, HARAs and AutoML diagrams so they can be opened directly. Architecture objects can now be resized either by editing width and height values or by dragging the red handles that appear when an item is selected. Fork and join bars keep a constant thickness so only their length changes.

## Workflow Overview

The diagram below illustrates how information flows through the major work products. Each box lists the main inputs and outputs so you can see how analyses feed into one another and where the review workflow fits. Approved reviews update the ASIL values propagated throughout the model.

```mermaid
flowchart TD
    subgraph ext [External inputs]
        X([BOM])
    end
    X --> R([Reliability analysis<br/>inputs: BOM<br/>outputs: FIT rates & parts])
    A([System functions & architecture]) --> B([HAZOP<br/>inputs: functions<br/>outputs: malfunctions])
    B --> C([HARA<br/>inputs: malfunctions<br/>outputs: hazards, ASIL, safety goals])
    A --> D([FMEA / FMEDA<br/>inputs: architecture, malfunctions, reliability<br/>outputs: failure modes])
    R --> D
    C --> D
    C --> E([FTA<br/>inputs: hazards & safety goals<br/>outputs: fault trees])
    D --> E
    E --> F([Safety requirements<br/>inputs: fault trees & failure modes])
    F --> G([Peer/Joint review<br/>inputs: requirements & analyses<br/>outputs: approved changes])
    G --> H([ASIL propagation to SGs, FMEAs and FTAs])
```

The workflow begins by entering system functions and architecture elements. A **BOM** is imported into a **Reliability analysis** which produces FIT rates and component lists used by the **FMEA/FMEDA** tables. A **HAZOP** analysis identifies malfunctions which become inputs to the **HARA** and FMEAs. The HARA assigns hazards and ASIL ratings to safety goals which then inform FMEDAs and **FTA** diagrams. Fault trees and failure modes generate safety requirements that go through peer or joint **reviews**. When a review is approved any changes to requirements or analyses automatically update the ASIL values traced back to the safety goals, FMEAs and FTAs.

## HAZOP Analysis

The **HAZOP Analysis** window lets you list system functions with one or more associated malfunctions. Each entry records the malfunction guideword (*No/Not*, *Unintended*, *Excessive*, *Insufficient* or *Reverse*), the related scenario, driving conditions and hazard, and whether it is safety relevant. Covered malfunctions may reference other entries as mitigation. When a function is allocated to an active component in a reliability analysis, its malfunctions become selectable failure modes in the FMEDA table.

## HARA Analysis

The **HARA Analysis** view builds on the safety relevant malfunctions from one or more selected HAZOPs. When creating a new HARA you can pick multiple HAZOP documents; only malfunctions from those selections appear in the table. Each HARA table contains the following columns:

1. **Malfunction** – combo box listing malfunctions flagged as safety relevant in the chosen HAZOP documents.
2. **Hazard** – textual description of the resulting hazard.
3. **Severity** – ISO&nbsp;26262 severity level (1–3).
4. **Severity Rationale** – free text explanation for the chosen severity.
5. **Controllability** – ISO&nbsp;26262 controllability level (1–3).
6. **Controllability Rationale** – free text explanation for the chosen controllability.
7. **Exposure** – ISO&nbsp;26262 exposure level (1–4).
8. **Exposure Rationale** – free text explanation for the chosen exposure.
9. **ASIL** – automatically calculated from severity, controllability and exposure using the ISO&nbsp;26262 risk graph.
10. **Safety Goal** – combo box listing all defined safety goals in the project.

The calculated ASIL from each row is propagated to the referenced safety goal so that inherited ASIL levels appear consistently in all analyses and documentation, including FTA top level events.

The **Hazard Explorer** window lists all hazards from every HARA in a read-only table for quick review or CSV export.

## Requirements Creation and Management

Safety requirements are defined directly on FTA nodes and FMEA entries. In the edit dialog for a node or table row use **Add New** to create a fresh requirement or **Add Existing** to reuse one from the global registry. A new requirement records an ID, type (vehicle or operational), ASIL and descriptive text. Requirements can be split into two with the **Decompose** button which assigns ASIL values according to ISO 26262 decomposition rules. All requirements are stored in a project-wide list so they can be attached to multiple elements.

Open the **Requirements Matrix** from the Requirements menu to see every requirement with its allocation to basic events and any traced safety goals. The matrix view links to a **Requirements Editor** where you can add, edit or delete entries and modify traceability. Requirement statuses automatically change from draft to *in review*, *peer reviewed*, *pending approval* and finally *approved* as associated reviews progress. Updating a requirement reopens affected reviews so feedback is always tracked against the latest version.

## AutoML Diagrams and Safety Analyses

Use case, activity, block and internal block diagrams can be created from the **Architecture** menu. Diagrams are stored inside a built-in SysML repository and appear in the *Analyses* explorer tab so they can be reopened alongside FMEAs and other documents. Each object keeps its saved size and properties so layouts remain stable when returning to the project.

Activity diagrams list individual **actions** that describe the expected behavior for a block. These actions can be referenced directly in HAZOP tables as potential malfunctions. When a block is linked to a circuit, any actions in its internal block diagram are inherited as additional failure modes for that circuit. The inherited actions automatically show up in new FMEDA tables along with the failure modes already defined for the circuit's components.

Elements on a diagram may reference reliability analyses. Choosing a **circuit** or **component** automatically fills the **fit**, **qualification** and **failureModes** fields using data from FMEA and FMEDA tables. These values show up in a *Reliability* compartment for blocks or below parts. When a block references a circuit, the components from that circuit's BOM can be inserted as parts in the linked internal block diagram with their failure modes already listed.

Requirements can also be attached to diagram elements to keep architecture and safety analyses synchronized. The same safety goals referenced in HAZOP or HARA tables can therefore be traced directly to the blocks and parts that implement them.

## BOM Integration with AutoML Diagrams

Blocks in block diagrams may reference circuits defined in a saved BOM via the new **circuit** property while parts reference individual components using the **component** property. Both element types also provide **fit**, **qualification** and **failureModes** attributes. Entering values for these fields shows them in a *Reliability* compartment for blocks or as additional lines beneath parts so FIT rates and qualification information remain visible in the AutoML model. When editing a block or part you can now pick from drop-down lists containing all circuits or components from saved reliability analyses. Selecting an item automatically fills in its FIT rate, qualification certificate and any failure modes found in FMEA tables.

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

* **FI2TC Analysis** – links each functional insufficiency to the triggering conditions, scenarios and mitigation measures that reveal the hazard.
* **TC2FI Analysis** – starts from the triggering condition and lists the impacted functions, architecture elements and related insufficiencies.

HARA values such as severity and the associated safety goal flow into these tables so SOTIF considerations remain connected to the overall risk assessment. Minimal cut sets calculated from the FTAs highlight combinations of FIs and TCs that form *CTAs*. From a CTA entry you can generate a functional modification requirement describing how the design must change to avoid the unsafe behaviour.

All FI2TC and TC2FI documents appear under the **Analyses** tab so they can be opened alongside HARA tables, FTAs and CTAs for a complete view of functional safety and SOTIF issues.

## Review Toolbox

Launch the review features from the **Review** menu:

* **Start Peer Review** – create at least one moderator and one reviewer, then tick the checkboxes for the FTAs and FMEAs you want to include. Each moderator and participant has an associated email address. A due date is requested and once reached the review becomes read‑only unless a moderator extends it. A document window opens showing the selected elements. FTAs are drawn on canvases you can drag and scroll, while FMEAs appear as full tables listing every field so failures can be reviewed line by line. Linked requirements are listed below and any text changes are colored the same way as other differences. Changes to which requirements are allocated to each item are highlighted in blue and red.
* **Start Joint Review** – add participants with reviewer or approver roles and at least one moderator, select the desired FTAs and FMEAs via checkboxes and enter a unique review name and description. Approvers can approve only after all reviewers are done and comments resolved. Moderators may edit the description, due date or participant list later from the toolbox. The document window behaves the same as for peer reviews with draggable FTAs and tabulated FMEAs. Requirement diffs are also shown in this view.
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
or reinstalling SciPy.


## Version History
- 0.1.2 - Clarified systems safety focus in description and About dialog.
- 0.1.1 - Updated description and About dialog.
- 0.1.0 - Added Help menu and version tracking.
