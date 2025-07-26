# Author: Miguel Marina <karel.capek.robotics@gmail.com>
from dataclasses import dataclass, field

@dataclass
class DiagnosticMechanism:
    """Diagnostic mechanism from ISO 26262-5 Annex D."""
    name: str
    coverage: float
    description: str = ""

@dataclass
class MechanismLibrary:
    """Collection of diagnostic mechanisms."""
    name: str
    mechanisms: list = field(default_factory=list)

# Complete list of diagnostic mechanisms from ISO 26262-5:2018 Annex D
ANNEX_D_MECHANISMS = [
    DiagnosticMechanism(
        "CRC",
        0.99,
        "Information redundancy using cyclic redundancy codes to detect data corruption during communication.",
    ),
    DiagnosticMechanism(
        "Watchdog",
        0.9,
        "Independent timer supervising program flow and triggering a safe state if not refreshed as expected.",
    ),
    DiagnosticMechanism(
        "Parity",
        0.8,
        "Single-bit hardware redundancy to detect odd-bit errors in a data stream.",
    ),
    DiagnosticMechanism(
        "Heartbeat",
        0.85,
        "Regular status message used to ensure communication peers are alive and responsive.",
    ),
    DiagnosticMechanism(
        "Range check",
        0.9,
        "Verification that signal values stay within predefined valid limits.",
    ),
    DiagnosticMechanism(
        "Failure detection by on-line monitoring",
        0.6,
        "D.2.1.1 Detect failures by monitoring system behaviour during operation.",
    ),
    DiagnosticMechanism(
        "Comparator",
        0.9,
        "D.2.1.2 Compare outputs of independent channels to detect discrepancies.",
    ),
    DiagnosticMechanism(
        "Majority voter",
        0.9,
        "D.2.1.3 Use majority voting to mask and detect channel failures.",
    ),
    DiagnosticMechanism(
        "Dynamic principles",
        0.75,
        "D.2.2.1 Force change of static signals to detect failures.",
    ),
    DiagnosticMechanism(
        "Analogue monitoring of digital signals",
        0.6,
        "D.2.2.2 Evaluate digital signals on an analogue level to detect illegal values.",
    ),
    DiagnosticMechanism(
        "Self-test by software cross exchange",
        0.75,
        "D.2.3.3 Independent units perform self-tests and exchange results.",
    ),
    DiagnosticMechanism(
        "Failure detection by on-line monitoring (electrical)",
        0.9,
        "Table D.3 Monitor electrical elements during operation.",
    ),
    DiagnosticMechanism(
        "Self-test by software (limited patterns)",
        0.75,
        "D.2.3.1 Software self-test using limited patterns.",
    ),
    DiagnosticMechanism(
        "Self-test supported by hardware",
        0.75,
        "D.2.3.2 Hardware assisted self-test for processing units.",
    ),
    DiagnosticMechanism(
        "Software diversified redundancy",
        0.9,
        "D.2.3.4 Two diverse software implementations in one channel.",
    ),
    DiagnosticMechanism(
        "Reciprocal comparison by software",
        0.9,
        "D.2.3.5 Two units exchange and compare results.",
    ),
    DiagnosticMechanism(
        "HW redundancy",
        0.9,
        "D.2.3.6 Redundant hardware such as dual core lockstep.",
    ),
    DiagnosticMechanism(
        "Configuration register test",
        0.9,
        "D.2.3.7 Verify configuration registers against expected values.",
    ),
    DiagnosticMechanism(
        "Stack over/under flow detection",
        0.6,
        "D.2.3.8 Detect violations of stack boundaries.",
    ),
    DiagnosticMechanism(
        "Integrated hardware consistency monitoring",
        0.9,
        "D.2.3.9 Use processor hardware exceptions to detect illegal conditions.",
    ),
    DiagnosticMechanism(
        "Failure detection by on-line monitoring (I/O)",
        0.6,
        "Table D.5 Monitor digital I/O during operation.",
    ),
    DiagnosticMechanism(
        "Test pattern",
        0.9,
        "D.2.4.1 Cyclical test of I/O or sensors using known patterns.",
    ),
    DiagnosticMechanism(
        "Code protection for digital I/O",
        0.75,
        "D.2.4.2 Use information or time redundancy on I/O signals.",
    ),
    DiagnosticMechanism(
        "Multi-channel parallel output",
        0.9,
        "D.2.4.3 Independent outputs compared externally.",
    ),
    DiagnosticMechanism(
        "Monitored outputs",
        0.9,
        "D.2.4.4 Compare outputs with independent inputs within a tolerance range.",
    ),
    DiagnosticMechanism(
        "Input comparison/voting",
        0.9,
        "D.2.4.5 Compare redundant inputs (1oo2, 2oo3, etc.).",
    ),
    DiagnosticMechanism(
        "One-bit hardware redundancy",
        0.6,
        "D.2.5.1 Parity bit to detect odd-bit failures on a bus.",
    ),
    DiagnosticMechanism(
        "Multi-bit hardware redundancy",
        0.75,
        "D.2.5.2 Block codes such as CRC or Hamming.",
    ),
    DiagnosticMechanism(
        "Read back of sent message",
        0.75,
        "D.2.5.9 Transmitter reads message from bus for comparison.",
    ),
    DiagnosticMechanism(
        "Complete hardware redundancy",
        0.9,
        "D.2.5.3 Duplicate bus channels for comparison.",
    ),
    DiagnosticMechanism(
        "Inspection using test patterns",
        0.9,
        "D.2.5.4 Cyclical test of data paths with predefined patterns.",
    ),
    DiagnosticMechanism(
        "Transmission redundancy",
        0.75,
        "D.2.5.5 Send information several times in sequence.",
    ),
    DiagnosticMechanism(
        "Information redundancy",
        0.75,
        "D.2.5.6 Attach checksum or CRC to transmitted data.",
    ),
    DiagnosticMechanism(
        "Frame counter",
        0.75,
        "D.2.5.7 Counter in each frame to detect loss or non-refreshment.",
    ),
    DiagnosticMechanism(
        "Timeout monitoring",
        0.75,
        "D.2.5.8 Monitor time between received messages.",
    ),
    DiagnosticMechanism(
        "Combined comm. monitoring",
        0.9,
        "Combination of information redundancy, frame counter and timeout monitoring (D.2.5.6-8).",
    ),
    DiagnosticMechanism(
        "Voltage or current control (input)",
        0.6,
        "D.2.6.1 Monitor input voltage or current values.",
    ),
    DiagnosticMechanism(
        "Voltage or current control (output)",
        0.9,
        "D.2.6.2 Monitor output voltage or current values.",
    ),
    DiagnosticMechanism(
        "Watchdog without time-window",
        0.6,
        "D.2.7.1 External watchdog triggered periodically.",
    ),
    DiagnosticMechanism(
        "Watchdog with time-window",
        0.75,
        "D.2.7.2 Watchdog with lower and upper triggering limits.",
    ),
    DiagnosticMechanism(
        "Logical programme sequence monitoring",
        0.75,
        "D.2.7.3 Monitor correct sequence of programme sections.",
    ),
    DiagnosticMechanism(
        "Temporal and logical monitoring",
        0.9,
        "D.2.7.4 Combine temporal facilities with logical checks.",
    ),
    DiagnosticMechanism(
        "Temporal, logical monitoring with time dependency",
        0.9,
        "D.2.7.5 Programme flow monitoring with relative time windows.",
    ),
    DiagnosticMechanism(
        "Sensor valid range",
        0.6,
        "D.2.8.1 Detect sensor shorts or opens using out-of-range values.",
    ),
    DiagnosticMechanism(
        "Sensor correlation",
        0.9,
        "D.2.8.2 Compare redundant sensors for drift or offsets.",
    ),
    DiagnosticMechanism(
        "Sensor rationality check",
        0.75,
        "D.2.8.3 Compare diverse sensors using a model.",
    ),
    DiagnosticMechanism(
        "Actuator monitoring",
        0.9,
        "D.2.9.1 Monitor actuator operation or feedback for coherence.",
    ),
]
