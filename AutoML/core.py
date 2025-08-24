import re
import math
import sys
import json
import tkinter as tk
from typing import Any, Optional
from tkinter import ttk, filedialog, simpledialog, scrolledtext
from gui.dialog_utils import askstring_fixed
from gui import messagebox, logger, add_treeview_scrollbars
from gui.button_utils import enable_listbox_hover_highlight
from gui.tooltip import ToolTip
from gui.style_manager import StyleManager
from gui.review_toolbox import (
    ReviewToolbox,
    ReviewData,
    ReviewParticipant,
    ReviewComment,
    ParticipantDialog,
    EmailConfigDialog,
    ReviewScopeDialog,
    UserSelectDialog as ReviewUserSelectDialog,
    ReviewDocumentDialog,
    VersionCompareDialog,
)
from functools import partial
from gui.safety_management_toolbox import SafetyManagementToolbox
from gui.gsn_explorer import GSNExplorer
from gui.safety_management_explorer import SafetyManagementExplorer
from gui.safety_case_explorer import SafetyCaseExplorer
from gui.gsn_diagram_window import GSNDiagramWindow, GSN_WINDOWS
from gui.causal_bayesian_network_window import CBN_WINDOWS
from gui.gsn_config_window import GSNElementConfig
from gui.search_toolbox import SearchToolbox
from gsn import GSNDiagram, GSNModule
from gsn.nodes import GSNNode, ALLOWED_AWAY_TYPES
from gui.closable_notebook import ClosableNotebook
from gui.icon_factory import create_icon
from gui.splash_screen import SplashScreen
from gui.mac_button_style import (
    apply_translucid_button_style,
    apply_purplish_button_style,
)
from dataclasses import asdict
from pathlib import Path
from analysis.mechanisms import (
    DiagnosticMechanism,
    MechanismLibrary,
    ANNEX_D_MECHANISMS,
    PAS_8800_MECHANISMS,
)
from config import load_diagram_rules, load_report_template
from analysis.requirement_rule_generator import regenerate_requirement_patterns
from pathlib import Path
from collections.abc import Mapping
import csv
try:
    from openpyxl import load_workbook
except Exception:  # openpyxl may not be installed
    load_workbook = None
from gui.drawing_helper import FTADrawingHelper, fta_drawing_helper
from analysis.user_config import (
    load_user_config,
    save_user_config,
    set_current_user,
    load_all_users,
    set_last_user,
    CURRENT_USER_NAME,
    CURRENT_USER_EMAIL,
)
from analysis.risk_assessment import (
    DERIVED_MATURITY_TABLE,
    ASSURANCE_AGGREGATION_AND,
    AND_DECOMPOSITION_TABLE,
    OR_DECOMPOSITION_TABLE,
    boolify,
    AutoMLHelper,
)
from analysis.models import (
    MissionProfile,
    ReliabilityComponent,
    ReliabilityAnalysis,
    HazopEntry,
    HaraEntry,
    HazopDoc,
    HaraDoc,
    StpaEntry,
    StpaDoc,
    FI2TCDoc,
    TC2FIDoc,
    DamageScenario,
    ThreatScenario,
    AttackPath,
    FunctionThreat,
    ThreatEntry,
    ThreatDoc,
    QUALIFICATIONS,
    COMPONENT_ATTR_TEMPLATES,
    RELIABILITY_MODELS,
    component_fit_map,
    ASIL_LEVEL_OPTIONS,
    ASIL_ORDER,
    ASIL_TARGETS,
    ASIL_TABLE,
    ASIL_DECOMP_SCHEMES,
    calc_asil,
    global_requirements,
    ensure_requirement_defaults,
    REQUIREMENT_TYPE_OPTIONS,
    REQUIREMENT_WORK_PRODUCTS,
    CAL_LEVEL_OPTIONS,
    CybersecurityGoal,
    CyberRiskEntry,
)
from gui.safety_case_table import SafetyCaseTable
from gui.architecture import (
    UseCaseDiagramWindow,
    ActivityDiagramWindow,
    BlockDiagramWindow,
    InternalBlockDiagramWindow,
    ControlFlowDiagramWindow,
    GovernanceDiagramWindow,
    ArchitectureManagerDialog,
    parse_behaviors,
    link_requirement_to_object,
    unlink_requirement_from_object,
    link_requirements,
    unlink_requirements,
    ARCH_WINDOWS,
)
from sysml.sysml_repository import SysMLRepository
from analysis.fmeda_utils import compute_fmeda_metrics
from analysis.scenario_description import template_phrases
import copy
import tkinter.font as tkFont
import builtins
builtins.REQUIREMENT_WORK_PRODUCTS = REQUIREMENT_WORK_PRODUCTS
builtins.SafetyCaseTable = SafetyCaseTable
try:
    from PIL import Image, ImageDraw, ImageFont
except ModuleNotFoundError:
    Image = ImageDraw = ImageFont = None
import os
import types
os.environ["GS_EXECUTABLE"] = r"C:\Program Files\gs\gs10.04.0\bin\gswin64c.exe"
import networkx as nx
# Import ReportLab for PDF export.
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
from gui.style_editor import StyleEditor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, SimpleDocTemplate, Image as RLImage
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO, StringIO
from email.utils import make_msgid
import html
import datetime
try:
    import PIL.Image as PILImage
except ModuleNotFoundError:
    PILImage = None
try:
    from reportlab.platypus import LongTable
except Exception:  # pragma: no cover - fallback when reportlab missing
    LongTable = None
from email.message import EmailMessage
import smtplib
import socket
styles = getSampleStyleSheet()  # Create the stylesheet.
preformatted_style = ParagraphStyle(name="Preformatted", fontName="Courier", fontSize=10)
if hasattr(styles, "add"):
    styles.add(preformatted_style)
else:  # pragma: no cover - fallback for minimal stubs
    styles["Preformatted"] = preformatted_style
# Characters used to display pass/fail status in metrics labels.
from analysis.constants import CHECK_MARK, CROSS_MARK
from analysis.utils import (
    append_unique_insensitive,
    derive_validation_target,
    exposure_to_probability,
    controllability_to_probability,
    severity_to_probability,
    update_probability_tables,
    EXPOSURE_PROBABILITIES,
    CONTROLLABILITY_PROBABILITIES,
    SEVERITY_PROBABILITIES,
    normalize_probability_mapping,
)
from analysis.safety_management import SafetyManagementToolbox, ACTIVE_TOOLBOX
from analysis.causal_bayesian_network import CausalBayesianNetwork, CausalBayesianNetworkDoc
from gui.toolboxes import (
    ReliabilityWindow,
    FI2TCWindow,
    HazopWindow,
    RiskAssessmentWindow,
    TC2FIWindow,
    HazardExplorerWindow,
    RequirementsExplorerWindow,
    DiagramElementDialog,
    _RequirementRelationDialog,
)
from gui.stpa_window import StpaWindow
from gui.threat_window import ThreatWindow
def format_requirement(req, include_id=True):
    """Return a formatted requirement string without empty ASIL/CAL fields."""
    parts = []
    if include_id and req.get("id"):
        parts.append(f"[{req['id']}]")
    if req.get("req_type"):
        parts.append(f"[{req['req_type']}]")
    asil = req.get("asil")
    if asil:
        parts.append(f"[{asil}]")
    cal = req.get("cal")
    if cal:
        parts.append(f"[{cal}]")
    parts.append(req.get("text", ""))
    return " ".join(parts)
from pathlib import Path
def get_version() -> str:
    """Read the tool version from the first line of README.md.
    The README is located alongside this file so we resolve the path relative
    to ``__file__``.  This avoids returning ``"Unknown"`` when the current
    working directory is different (e.g. when launching from another folder or
    from an installed package).
    """
    try:
        readme = Path(__file__).resolve().parent / "README.md"
        with readme.open("r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            if first_line.lower().startswith("version:"):
                return first_line.split(":", 1)[1].strip()
    except Exception:
        pass
    return "Unknown"
VERSION = get_version()
# Contact information for splash screen
AUTHOR = "Miguel Marina"
AUTHOR_EMAIL = "karel.capek.robotics@gmail.com"
AUTHOR_LINKEDIN = "https://www.linkedin.com/in/progman32/"
# Target PMHF limits per ASIL level (events per hour)
PMHF_TARGETS = {
    "D": 1e-8,
    "C": 1e-7,
    "B": 1e-7,
    "A": 1e-6,
    "QM": 1.0,
}
##########################################
# VALID_SUBTYPES dictionary
##########################################
VALID_SUBTYPES = {
    "Confidence": ["Function", "Human Task"],
    "Robustness": ["Function", "Human Task"],
    "Maturity": ["Functionality"],
    "Rigor": ["Failure", "AI Error", "Functional Insufficiency"],
    "Prototype Assurance Level (PAL)": ["Vehicle Level Function"]
}
# Node types treated as gates when rendering and editing
_CONFIG_PATH = Path(__file__).resolve().parent / "config/diagram_rules.json"
_CONFIG = load_diagram_rules(_CONFIG_PATH)
GATE_NODE_TYPES = set(_CONFIG.get("gate_node_types", []))
_PATTERN_PATH = Path(__file__).resolve().parent / "config/requirement_patterns.json"
_REPORT_TEMPLATE_PATH = (
    Path(__file__).resolve().parent / "config/product_report_template.json"
)
def _reload_local_config() -> None:
    """Reload gate node types from the external configuration file."""
    global _CONFIG, GATE_NODE_TYPES
    _CONFIG = load_diagram_rules(_CONFIG_PATH)
    GATE_NODE_TYPES = set(_CONFIG.get("gate_node_types", []))
    # Regenerate requirement patterns whenever diagram rules change
    regenerate_requirement_patterns()
##########################################
# Global Unique ID Counter for Nodes
##########################################
unique_node_id_counter = 1
import uuid
dynamic_recommendations = {
    1: {
        "Testing Requirements": (
            "Perform extensive scenario-based simulations covering normal driving, sensor failures, emergency braking, "
            "and boundary conditions. Conduct rigorous lab tests and closed-course trials to verify core ADS functions under ideal conditions. "
            "No public road tests are permitted until every core function is validated in a controlled prototype environment."
        ),
        "IFTD Responsibilities": (
            "A dedicated safety driver is in the vehicle at all times along with an engineer. The IFTD must be able to take immediate manual control "
            "when abnormal conditions are detected. Training focuses on achieving short reaction times and enhanced situational awareness through frequent emergency takeover drills."
        ),
        "Preventive Maintenance Actions": (
            "Conduct pre-trip and post-trip inspections on every run. Regularly calibrate, clean, and realign all sensors (cameras, radar, LiDAR). "
            "Maintain a detailed log and perform daily component checks to promptly address any anomalies before further testing."
        ),
        "Relevant AVSC Guidelines": (
            "Adhere to AVSC Best Practice for In-Vehicle clone Test Driver Selection, Training, and Oversight (AVSC00001-2019) and SAE J3018 guidelines, "
            "with extra emphasis on ensuring the IFTD can safely intervene in a prototype environment."
        ),
        "Extra Recommendations": {
            "steering": (
                "Include operational tests that simulate sudden, unintended steering inputs and verify that dynamic steering limiters are active. "
                "Ensure that the IFTD can promptly override any abnormal steering commands."
            ),
            "lateral": (
                "Design tests to simulate faulty lateral control (e.g., drifting or incorrect lane-keeping) and verify that any deviation is corrected within safe lateral boundaries. "
                "These tests shall include simulations, closed-course testing, and silent mode testing as required by the system’s rigor and child maturity."
            ),
            "longitudinal": (
                "Simulate sudden acceleration or deceleration events and verify that smooth speed transitions are maintained. "
                "Ensure that any unexpected longitudinal changes are managed safely by the IFTD."
            ),
            "braking": (
                "Simulate unintended or excessive braking events on a closed course and verify that the IFTD can quickly restore controlled braking and vehicle stability. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "deceleration": (
                "Develop test scenarios where deceleration is either too abrupt or delayed, and verify that the IFTD's intervention results in smooth, predictable slowdowns within defined limits."
            ),
            "acceleration": (
                "Test for unintended acceleration surges by simulating load changes and external disturbances. "
                "Verify that the IFTD can promptly override acceleration commands to maintain smooth, safe speed profiles."
            ),
            "park brake": (
                "Design controlled tests that trigger parking brake faults and verify that the system engages/disengages reliably. "
                "Ensure that the IFTD can safely manage the vehicle during such events."
            ),
            "parking brake": (
                "Conduct targeted tests simulating parking brake malfunctions, ensuring reliable engagement/disengagement and that the IFTD can intervene safely."
            ),
            "mode": (
                "Simulate mode indicator anomalies to verify that the IFTD receives clear, actionable alerts and can enforce proper system state transitions."
            ),
            "notification": (
                "Verify that the alert system responds accurately to simulated sensor or system errors in a controlled test environment. "
                "Ensure that alerts are displayed clearly via visual and auditory cues and are properly logged."
            ),
            "takeover": (
                "Simulate scenarios where the ADS disengages unexpectedly, requiring the IFTD to take over. "
                "Validate that the takeover mechanism enables the IFTD to quickly and safely assume manual control."
            ),
            "rollaway": (
                "Conduct basic simulation tests to verify that the system can detect a potential rollaway condition. "
                "Test the activation of emergency brakes and initial control protocols on a slight incline in a controlled laboratory environment."
            ),
            "control": (
                "Assess the IFTD’s basic manual override capability under simulated conditions. "
                "Ensure that, despite minimal training, the driver can momentarily assume control in a laboratory environment."
            )
        }
    },
    2: {
        "Testing Requirements": (
            "Initiate limited public-road tests under tightly controlled conditions (e.g., low-speed, daylight, good weather) within a constrained ODD. "
            "Employ advanced simulations—including fault injection, emergency braking, and scenario-based tests—alongside closed-course validations to verify safe operation."
        ),
        "IFTD Responsibilities": (
            "The safety driver (with a co-driver if necessary) continuously monitors the ADS and is ready to intervene immediately. "
            "Training drills focus on rapid manual intervention and maintaining situational awareness under varying test conditions."
        ),
        "Preventive Maintenance Actions": (
            "Implement both time-based and event-triggered inspections. Prior to each test, verify that sensor calibrations and system integrity meet safety standards. "
            "Document all findings comprehensively and address any anomalies immediately to support safe operation."
        ),
        "Relevant AVSC Guidelines": (
            "Follow AVSC Best Practice for Data Collection for ADS-DVs (AVSC00004-2020), comply with SAE J3018, and meet local regulatory standards, "
            "with a focus on enhancing IFTD control and training."
        ),
        "Extra Recommendations": {
            "steering": (
                "Design tests that simulate unexpected steering deviations and verify that the IFTD can safely override these inputs. "
                "These tests shall include simulations, closed-course testing, and silent mode testing as per the required rigor and maturity of child elements."
            ),
            "lateral": (
                "Simulate faulty lateral control scenarios to ensure that any drift or deviation is corrected by the IFTD within safe lateral boundaries. "
                "These tests shall include simulations, closed-course testing, and silent mode testing as required by the system’s rigor and maturity of child elements."
            ),
            "longitudinal": (
                "Incorporate scenarios that simulate sudden acceleration or deceleration events. "
                "Verify that the emergency override system responds to maintain safe speed profiles."
            ),
            "braking": (
                "Include tests that simulate unintended or excessive braking events and verify that the IFTD can quickly re-establish controlled braking. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "deceleration": (
                "Develop test scenarios to confirm that deceleration remains controlled, even if it is slightly delayed or abrupt. "
                "Verify that basic emergency intervention protocols are activated in a controlled environment."
            ),
            "acceleration": (
                "Test for unintended acceleration surges by simulating moderate load changes and external disturbances. "
                "Confirm that the emergency override system responds to maintain safe speed profiles."
            ),
            "park brake": (
                "Conduct controlled tests to simulate parking brake faults and verify that basic safety protocols, such as system alerts and initial brake engagement, function properly."
            ),
            "parking brake": (
                "Conduct controlled tests to simulate parking brake malfunctions and ensure that the system engages protective measures reliably."
            ),
            "mode": (
                "Simulate mode indicator anomalies to verify that the IFTD receives clear alerts and can trigger preliminary system checks."
            ),
            "notification": (
                "Test the alert system under controlled conditions to verify prompt and clear notification of sensor or system errors."
            ),
            "takeover": (
                "Simulate scenarios where the ADS unexpectedly disengages to ensure that the IFTD can assume manual control quickly."
            ),
            "rollaway": (
                "Perform controlled closed-course tests simulating a rollaway event on a mild slope. "
                "Validate that the emergency braking system engages, the transmission shifts to neutral, and that driver alerts are issued promptly."
            ),
            "control": (
                "Verify that the IFTD can take control during simple, low-speed scenarios. "
                "Ensure that the manual override interface provides clear signals for intervention under these controlled conditions."
            )
        }
    },
    3: {
        "Testing Requirements": (
            "Expand testing into a broader ODD using high-fidelity simulations and extended on-road trials. "
            "Include scenarios such as higher speeds, nighttime driving, and light rain, along with targeted fault-injection tests that challenge the ADS and verify that the IFTD can promptly intervene."
        ),
        "IFTD Responsibilities": (
            "The safety driver remains onboard as a continuous clone while the ADS handles most of the route. "
            "Enhanced training emphasizes rapid manual takeover and precise interpretation of ADS signals, reinforced by regular simulator and on-track drills."
        ),
        "Preventive Maintenance Actions": (
            "Establish a formal maintenance schedule combining regular and event-based inspections supported by on-board diagnostics and predictive analytics. "
            "Preemptively address any component degradation to ensure that the IFTD’s ability to intervene is never compromised."
        ),
        "Relevant AVSC Guidelines": (
            "Utilize AVSC Best Practice for Metrics and Methods for Assessing Safety Performance and continuous monitoring principles. "
            "Ensure periodic IFTD re-training and adhere to ISO 26262/21448 for functional safety."
        ),
        "Extra Recommendations": {
            "steering": (
                "Simulate abnormal steering responses and verify that the IFTD can override these inputs safely. "
                "These tests shall include simulations, closed-course testing, and silent mode testing as per the required rigor and the maturity of child elements."
            ),
            "lateral": (
                "Develop test scenarios that replicate lateral control failures and verify that the IFTD restores proper lateral stability within defined limits. "
                "These tests shall include simulations, closed-course testing, and silent mode testing as required by the system’s rigor and child maturity."
            ),
            "longitudinal": (
                "Design tests that simulate abrupt changes in speed and verify that manual override maintains smooth acceleration and deceleration within preset control limits. "
                "These tests shall include simulations, closed-course testing, and silent mode testing as required."
            ),
            "braking": (
                "Include tests for inconsistent braking responses and evaluate how quickly and effectively the IFTD can re-establish controlled braking within safe limits. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "deceleration": (
                "Test deceleration behavior under fault conditions, ensuring that even with anomalies the deceleration remains predictable and controllable. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "acceleration": (
                "Include scenarios that trigger unexpected acceleration surges and verify that the IFTD can promptly intervene to restore safe speed levels. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "park brake": (
                "Design tests that simulate parking brake faults and assess the IFTD's ability to safely manage the vehicle until normal operation is restored. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "parking brake": (
                "Design tests that simulate parking brake faults and assess the IFTD's ability to safely manage the vehicle until normal operation is restored. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "mode": (
                "Simulate mode indicator errors and confirm that the IFTD is alerted to enforce correct system state transitions. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "notification": (
                "During extended on-road trials, verify that the notification system integrates with live sensor data to produce real alerts. "
                "Ensure that alerts are clearly presented—via both visual and auditory channels—and that the IFTD can respond promptly under dynamic conditions. "
                "Also, conduct performance studies to assess the IFTD's alert perception, reaction time, and controllability."
            ),
            "takeover": (
                "Develop complex scenarios that require the IFTD to take over from the ADS during fault conditions. "
                "Monitor response time and the system’s ability to safely transition to manual control, and conduct detailed post-event analyses."
            ),
            "rollaway": (
                "Simulate a truck rollaway scenario on a declining grade under controlled conditions. "
                "Verify that the vehicle's emergency braking, transmission neutralization, and electronic stability controls engage promptly to prevent uncontrolled movement. "
                "Ensure that tests include driver override procedures and proper system logging for subsequent analysis."
            ),
            "control": (
                "Confirm that the IFTD consistently demonstrates the ability to assume control during operational tests. "
                "The manual override interface should be intuitive, providing timely feedback and clear signals to the driver."
            )
        }
    },
    4: {
        "Testing Requirements": (
            "Conduct pilot tests in a quasi-commercial setting on intended routes under realistic conditions. "
            "Test the ADS across its full ODD—including boundary scenarios—using advanced simulations and on-road trials designed to safely challenge system limits."
        ),
        "IFTD Responsibilities": (
            "An IFTD is onboard at all times as the ultimate safety net. Although interventions become less frequent, the driver must remain vigilant and undergo regular drills "
            "and attention tests to ensure sustained manual control readiness under operational conditions."
        ),
        "Preventive Maintenance Actions": (
            "Integrate comprehensive preventive maintenance into the test cycle. Perform extensive pre-run system checks (HD map verification, sensor cleaning, redundant system tests) "
            "to confirm that all components operate reliably, thereby supporting uninterrupted IFTD oversight."
        ),
        "Relevant AVSC Guidelines": (
            "Implement AVSC Best Practice for First Responder Interactions and adopt a standardized Safety Inspection Framework. "
            "Ensure continuous monitoring and compliance with regulatory requirements (e.g., FMCSA, state DOT), with extra emphasis on IFTD training and rapid intervention procedures."
        ),
        "Extra Recommendations": {
            "steering": (
                "Include operational tests verifying that unexpected steering deviations are safely managed by the IFTD, with control limits enforced. "
                "These tests shall include simulations, closed-course testing, and silent mode testing as required."
            ),
            "lateral": (
                "Simulate faulty lateral control scenarios and verify that any drift or deviation is corrected by the IFTD within safe lateral boundaries. "
                "These tests shall include simulations, closed-course testing, and silent mode testing as required by the system’s rigor and maturity of child elements."
            ),
            "longitudinal": (
                "Design tests that simulate abrupt or erratic longitudinal events. Verify that manual override smoothly restores safe acceleration and deceleration within predefined control limits. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "braking": (
                "Conduct tests simulating unintended or excessive braking events and verify that the IFTD can rapidly re-establish controlled braking with predictable deceleration. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "deceleration": (
                "Include scenarios that ensure deceleration remains smooth and within safe limits even under abnormal conditions, with timely IFTD intervention if needed. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "acceleration": (
                "Test for unexpected acceleration surges and verify that the IFTD can safely override to restore smooth acceleration within acceptable limits. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "park brake": (
                "Perform targeted tests on parking brake engagement under fault conditions to verify reliable operation and that the IFTD can safely manage the vehicle within defined control limits. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "parking brake": (
                "Perform targeted tests on parking brake engagement under fault conditions to verify reliable operation and that the IFTD can safely manage the vehicle within defined control limits. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "mode": (
                "Simulate mode indicator anomalies and verify that the IFTD receives clear, actionable alerts to enforce correct system state transitions, "
                "while ensuring control limits are maintained. These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "notification": (
                "During pilot operations, validate that the notification system generates real-time alerts in response to actual sensor malfunctions or system deviations. "
                "Ensure that alerts are unambiguous and use multiple modalities (visual and auditory) to prompt immediate manual intervention if required. "
                "Additionally, perform targeted studies to measure the IFTD's alert perception, reaction time, and controllability, and apply these insights to refine both the alert mechanisms and driver training protocols."
            ),
            "takeover": (
                "Conduct pilot tests that incorporate controlled takeover scenarios. Assess the responsiveness, accuracy, and smoothness of manual intervention when the ADS disengages. "
                "Measure key performance metrics such as takeover speed and transition stability, and use these data to further refine both the takeover mechanism and IFTD training protocols."
            ),
            "rollaway": (
                "Under more demanding conditions, simulate a truck rollaway on a steeper decline with higher speeds. "
                "Verify that advanced emergency protocols—including enhanced trailer locking mechanisms and improved driver alert systems—are activated. "
                "Ensure that the vehicle's redundant braking and stability control systems work in tandem, and that the system facilitates timely driver override if required."
            ),
            "control": (
                "Ensure that the IFTD reliably assumes control in complex scenarios. "
                "The system should deliver clear override signals, and the driver must demonstrate enhanced situational awareness and rapid response under challenging conditions."
            )
        }
    },
    5: {
        "Testing Requirements": (
            "Subject the ADS to rigorous edge-case validations and continuous simulation exercises that safely challenge the system across its entire ODD. "
            "Design test scenarios to deliberately trigger abnormal conditions so that control limits are enforced and the IFTD remains fully prepared to intervene."
        ),
        "IFTD Responsibilities": (
            "Even at the highest automation level, an IFTD is always onboard as a failsafe. Their role is primarily supervisory, yet they undergo continuous, intensive training "
            "and periodic drills—including attention-enhancing measures such as periodic system alerts—to ensure immediate manual control if any sensor or system fault occurs."
        ),
        "Preventive Maintenance Actions": (
            "Maintain standard commercial fleet maintenance protocols with automated self-checks and condition-based preventive measures. "
            "Conduct frequent system health verifications—including sensor recalibration, hardware diagnostics, and software integrity tests—to ensure that control limits are consistently maintained and the IFTD oversight remains uncompromised."
        ),
        "Relevant AVSC Guidelines": (
            "Implement all applicable AVSC best practices—including continuous monitoring, first responder protocols, and transparency standards. "
            "Adhere to industry certifications (e.g., ANSI/UL 4600, ISO 26262/21448) while emphasizing rigorous IFTD training, enhanced system controllability, and rapid manual intervention within defined control limits."
        ),
        "Extra Recommendations": {
            "steering": (
                "Include operational tests verifying that dynamic steering limiters are active and that the IFTD can safely intervene when steering inputs exceed defined control limits. "
                "These tests shall include simulations, closed-course testing, and silent mode testing as required."
            ),
            "lateral": (
                "Design tests to simulate faulty lateral control and verify that any drift or deviation is corrected by the IFTD within safe lateral boundaries. "
                "These tests shall include simulations, closed-course testing, and silent mode testing as required by the system’s rigor and the maturity of all child elements."
            ),
            "longitudinal": (
                "Develop scenarios that test the smooth manual override of acceleration and deceleration controls, ensuring that any unexpected longitudinal changes are managed within preset control limits. "
                "These tests shall include simulations, closed-course testing, and silent mode testing as required."
            ),
            "braking": (
                "Include test cases for unintended or excessive braking, confirming that the IFTD can immediately assume control to restore safe braking within defined limits. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "deceleration": (
                "Verify through operational tests that deceleration remains smooth and controlled even when system signals are abnormal, ensuring timely IFTD intervention within safe deceleration limits. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "acceleration": (
                "Include scenarios to detect and safely manage any unintended acceleration surges, ensuring the IFTD can quickly override to maintain smooth speed transitions within acceptable limits. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "park brake": (
                "Perform targeted tests on parking brake engagement under fault conditions to ensure reliable performance and that the IFTD can safely manage the vehicle within defined control limits. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "parking brake": (
                "Perform targeted tests on parking brake engagement under fault conditions to ensure reliable performance and that the IFTD can safely manage the vehicle within defined control limits. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "mode": (
                "Simulate mode indicator anomalies and verify that the IFTD receives clear, actionable alerts to enforce correct system state transitions while maintaining operational control limits. "
                "These tests shall include simulations, closed-course testing, and silent mode testing."
            ),
            "notification": (
                "Under near-commercial conditions, monitor the notification alert system over extended periods to ensure that alerts are consistently delivered in real-time. "
                "Validate that alerts are unambiguous and use multiple modalities (visual and auditory) to prompt immediate manual intervention if required. "
                "Furthermore, conduct comprehensive studies to quantify the IFTD’s alert perception time, reaction time, and controllability, and apply these insights to refine both the alert mechanisms and driver training programs."
            ),
            "takeover": (
                "Even in near-commercial conditions, periodically simulate takeover events to ensure that the ADS remains fail-safe and that the IFTD can effectively intervene if required. "
                "Measure key performance metrics—such as takeover speed, accuracy, and smoothness of transition—and use these data to continuously refine the takeover mechanisms and improve IFTD training."
            ),
            "rollaway": (
                "Conduct exhaustive tests under worst-case rollaway scenarios, such as extended, steep grades combined with sensor or system faults. "
                "Ensure that all redundant systems, including emergency braking, transmission neutralization, and electronic stability controls, engage seamlessly. "
                "Validate the effectiveness of automated driver override protocols and comprehensive system logging to support post-incident analysis."
            ),
            "control": (
                "Validate that the IFTD can seamlessly assume complete control even under worst-case conditions. "
                "Extensive driver training, robust override interfaces, and redundant manual control mechanisms must be confirmed during rigorous testing."
            )
        }
    }
}
AutoML_Helper = AutoMLHelper()
##########################################
# Edit Dialog 
##########################################
##########################################
# Main Application (Parent Diagram)
##########################################
##########################################
# Node Model 
##########################################
##########################################
# Page Diagram 
##########################################
def main():
    root = tk.Tk()
    # Prevent the main window from being resized so small that
    # widgets and toolbars become unusable.
    root.minsize(1200, 700)
    enable_listbox_hover_highlight(root)
    # Hide the main window while prompting for user info
    root.withdraw()
    # Show initialization splash screen
    SplashScreen(
        root,
        version=VERSION,
        author=AUTHOR,
        email=AUTHOR_EMAIL,
        linkedin=AUTHOR_LINKEDIN,
    ).wait_window()
    users = load_all_users()
    last_name, last_email = load_user_config()
    if users:
        dlg = UserSelectDialog(root, users, last_name)
        if dlg.result:
            name, email = dlg.result
            if name == "New User...":
                info = UserInfoDialog(root, "", "").result
                if info:
                    name, email = info
                    save_user_config(name, email)
            else:
                email = users.get(name, email)
                set_last_user(name)
    else:
        dlg = UserInfoDialog(root, last_name, last_email)
        if dlg.result:
            name, email = dlg.result
            save_user_config(name, email)
    set_current_user(name, email)
    # Create a fresh helper each session:
    global AutoML_Helper
    AutoML_Helper = AutoMLHelper()
    # Show and maximize the main window after login
    root.deiconify()
    try:
        root.state("zoomed")
    except tk.TclError:
        try:
            root.attributes("-zoomed", True)
        except tk.TclError:
            pass
    app = AutoMLApp(root)
    root.mainloop()
if __name__ == "__main__":
    main()