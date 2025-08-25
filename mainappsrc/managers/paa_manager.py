# Author: Miguel Marina <karel.capek.robotics@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2025 Capek System Safety & Robotic Solutions
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

"""
===============================================================================
Risk & Assurance Gate Calculator for Autonomous Systems
===============================================================================

Overview of the Provided Risk Assessment Approach
-------------------------------
This tool is a semi-quantitative method designed to assess the safety assurance 
of an autonomous system’s subsystems. It produces an Prototype Assurance Level (PAL) (on a scale 
from 1 to 5) using qualitative labels that describe the required level of safety 
measures. For example, the scale is defined as:

   1 → PAL1
   2 → PAL2
   3 → PAL3
   4 → PAL4
   5 → PAL5

The goal is to identify potential safety gaps and determine the extra assurance 
(i.e. additional testing, validation, design modifications) needed before a 
prototype is approved for public road trials.

Inputs – Confidence, Robustness, and Direct Assurance Metrics
-------------------------------
Each subsystem is evaluated using three main inputs (each rated from 1 to 5):

  1. **Confidence Level (CL):** Reflects the quality and extent of testing/validation.
  2. **Robustness Score (RS):** Reflects the strength of design safeguards and redundancy.
     (Different criteria are applied for system functions versus human tasks.)
  3. **Direct Assurance:** Pre-assessed assurance values derived from safety analyses.

For basic (leaf) nodes the provided ratings are used directly.

Computation Logic and Manual Calculation
-------------------------------

### 1. Deriving an Prototype Assurance Level (PAL) from Base Inputs
When only Confidence and Robustness values are provided, the tool “inverts” these 
inputs to yield a base Prototype Assurance Level (PAL). In this method, low confidence and low robustness
result in a high assurance requirement (i.e. “PAL5”), while high confidence and high robustness
yield a low assurance requirement (i.e. “PAL1”).

**Assurance Matrix for Base Inputs (Qualitative Labels)**

|                           | **Confidence: Level 1** | **Confidence: Level 2**   | **Confidence: Level 3** | **Confidence: Level 4** | **Confidence: Level 5** |
|---------------------------|---------------------------|-----------------------|--------------------------|----------------------|-----------------------|
| **Robustness: Level 1** | PAL5                     | PAL5                 | PAL4                     | PAL4                 | PAL4                  |
| **Robustness: Level 2**       | PAL5                     | PAL5                 | PAL4                     | PAL3                 | PAL3                  |
| **Robustness: Level 3**  | PAL4                      | PAL4                  | PAL3                 | PAL3             | PAL1             |
| **Robustness: Level 4**      | PAL4                      | PAL3              | PAL3                 | PAL1            | PAL1             |
| **Robustness: Level 5**     | PAL4                      | PAL3              | PAL1                | PAL1            | PAL1             |

*Interpretation:*
– Very poor testing and design (i.e. both "Level 1") lead to a “PAL5” assurance requirement.
– Excellent testing and design (i.e. both "Level 5") result in an “PAL1” requirement.
– Mixed values yield intermediate Prototype Assurance Levels (PAL).

---

### 2. Aggregating Prototype Assurance Levels (PAL) from Child Nodes

When a parent node aggregates Prototype Assurance Levels (PAL) from its children, the aggregation method 
depends on the logical gate connecting them:

#### For an **AND Gate**:
All components must be robust, so the overall assurance is determined by combining the child 
levels using a reliability-inspired approach. Use the following qualitative guideline:

**Aggregation Table for AND Gate (Qualitative Labels)**

|                         | **Child 2: Level 1** | **Child 2: Level 2**   | **Child 2: Level 3** | **Child 2: Level 4**   | **Child 2: Level 5**  |
|-------------------------|------------------------|--------------------|-----------------------|---------------------|---------------------|
| **Child 1: Level 1**  | PAL1              | PAL1          | PAL2                   | PAL4                | PAL5               |
| **Child 1: Level 2**        | PAL1              | PAL2                | PAL3              | PAL4                | PAL5               |
| **Child 1: Level 3**   | PAL2                    | PAL3           | PAL4                  | PAL5               | PAL5               |
| **Child 1: Level 4**       | PAL4                   | PAL4               | PAL5                 | PAL5               | PAL5               |
| **Child 1: Level 5**      | PAL5                  | PAL5              | PAL5                 | PAL5               | PAL5               |

*Interpretation:*
– Combining two "Level 5" components remains “PAL5.”
– If one component is significantly lower, the overall requirement shifts toward a higher assurance need.

#### For an **OR Gate**:
When alternative options are available, a simple average (by converting the qualitative levels
to an ordered scale) is used. A strong alternative (e.g. “PAL5”) can partially offset a weaker one
(e.g. “PAL2”).

---

### 3. Decomposing a Parent Prototype Assurance Level (PAL) into Child Targets

A parent node’s overall assurance requirement can be decomposed into target Prototype Assurance Levels (PAL) 
for its children. The following guidelines serve as a reference for common decompositions:

**Decomposition Guidelines**

- **Parent Assurance: PAL5**
  – Option A: Both children target “PAL4.”
  – Option B: One child may target “PAL5” while the other targets “PAL1” so that their combined effect meets the “PAL5” requirement.

- **Parent Assurance: PAL4**
  – Children should typically target between “PAL3” and “PAL4.”

- **Parent Assurance: PAL3**
  – Children should have targets in the range of “PAL2” to “PAL3.”

- **Parent Assurance: PAL2**
  – Children should target “PAL1” or “PAL2.”

- **Parent Assurance: PAL1**
  – Both children should be “PAL1.”

These rules ensure that when children’s Prototype Assurance Levels (PAL) are aggregated (using the AND or OR rules), 
they “reconstruct” the parent’s overall requirement.

---

### 4. Adjusting Assurance Based on Severity

Severity reflects the potential impact of a subsystem’s failure. It is used to adjust the computed 
Prototype Assurance Level (PAL) as follows:

- **General Rule (for most nodes):**  
  **Final Prototype Assurance Level (PAL) = (Aggregated Child Assurance + Highest Parent Severity) ÷ 2**  
  A higher severity (indicating more catastrophic consequences) increases the overall assurance requirement.

- **For Vehicle Level Functions:**  
  The node’s own severity is used instead of the parent’s. An example adjustment formula is:  
  **Adjusted Assurance = (2 × Computed Assurance) – (Node’s Own Severity)**  
  This modification increases the Prototype Assurance Level (PAL) when the potential impact is high.

---

### Discretization Tables
The following tables map raw numeric inputs to discrete levels that are then translated into qualitative labels:

1) **Confidence Level**

   +-------+------------------------+-----------------------------------------------+
   | Level | Description            | Expert Criteria                               |
   +-------+------------------------+-----------------------------------------------+
   |   1   | Very poor confidence   | No testing or validation evidence.           |
   |   2   | Poor confidence        | Minimal testing; incomplete evidence.        |
   |   3   | Moderate confidence    | Some validation; moderate evidence.          |
   |   4   | High confidence        | Well-tested with redundant checks.           |
   |   5   | Excellent confidence   | Comprehensive testing & strong evidence.     |
   +-------+------------------------+-----------------------------------------------+

2) **Robustness (Function)**

   +-------+--------------------------+---------------------------------------------+
   | Score | Description             | Rationale (Safety Loading)                  |
   +-------+--------------------------+---------------------------------------------+
   |   1   | Very Poor Safety Load   | Minimal redundancy; fails to mitigate risks.|
   |   2   | Poor Safety Load        | Only basic safety measures.                 |
   |   3   | Moderate Safety Load    | Standard protection; moderate redundancy.   |
   |   4   | High Safety Load        | Strong redundancy & mitigations.            |
   |   5   | Excellent Safety Load   | Full redundancy & comprehensive measures.   |
   +-------+--------------------------+---------------------------------------------+

3) **Robustness (Human Task)**

   +-------+--------------------------+----------------------------------------------+
   | Level | Description            | Expert Criteria for a Human Task             |
   +-------+--------------------------+----------------------------------------------+
   |   1   | Very poor performance  | Minimal training; slow reaction times.       |
   |   2   | Poor performance       | Limited training; suboptimal responses.      |
   |   3   | Moderate performance   | Adequately trained; acceptable reactions.    |
   |   4   | High performance       | Very experienced; quick & sound decisions.   |
   |   5   | Excellent performance  | Expert-level with flawless performance.      |
   +-------+--------------------------+----------------------------------------------+

---

### Summary of Qualitative Assurance Labels

- **PAL1:** Minimal assurance required (system is very safe).
- **PAL2:** Some assurance is required.
- **PAL3:** A moderate level of additional assurance is needed.
- **PAL4:** Significant additional assurance is required.
- **PAL5:** Maximum assurance is required (system is highly unsafe without improvements).

---

### Additional Notes on the Calculation Process

- **Combining Direct Inputs:**  
  If any direct assurance inputs are provided, they are combined using logical gate rules:
  
  - **OR Gate:** Inputs are averaged.
  - **AND Gate:** Inputs are combined using a “complement product” approach.

- **Adjustment with Severity:**  
  The final Prototype Assurance Level (PAL) is adjusted by incorporating the severity (using the highest parent severity unless the node is a Vehicle Level Function, in which case its own severity is used).

- **Decomposition and Aggregation:**  
  The parent node’s assurance requirement can be decomposed into target Prototype Assurance Levels (PAL) for its children (see Decomposition Guidelines above), and child Prototype Assurance Levels (PAL) are aggregated (using the AND/OR rules) to reconstruct the parent’s overall requirement.

-------------------------------
References
----------
- Rausand, M., & Høyland, A. (2004). *System Reliability Theory: Models, Statistical Methods, and Applications.* Wiley-Interscience.

===============================================================================
"""

"""Prototype Assurance Analysis utilities for AutoMLApp."""

import tkinter as tk


class PrototypeAssuranceManager:
    """Encapsulate Prototype Assurance Analysis operations."""

    def __init__(self, app: "AutoMLApp") -> None:
        self.app = app

    def enable_paa_actions(self, enabled: bool) -> None:
        """Enable or disable PAA-related menu actions."""
        if hasattr(self.app, "paa_menu"):
            state = tk.NORMAL if enabled else tk.DISABLED
            for key in ("add_confidence", "add_robustness", "add_gate"):
                self.app.paa_menu.entryconfig(
                    self.app._paa_menu_indices[key], state=state
                )

    def _create_paa_tab(self) -> None:
        """Convenience wrapper for creating a PAA diagram."""
        self.app._create_fta_tab("PAA")

    def create_paa_diagram(self) -> None:
        """Initialize a Prototype Assurance Analysis diagram and its top-level event."""
        self._create_paa_tab()
        self.app.add_top_level_event()
        if getattr(self.app, "paa_root_node", None):
            self.app.window_controllers.open_page_diagram(self.app.paa_root_node)
