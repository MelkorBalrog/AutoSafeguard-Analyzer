from dataclasses import dataclass, field
from typing import List

@dataclass
class SafetyWorkProduct:
    """Represents a deliverable created during a safety activity."""
    name: str
    source: str
    rationale: str = ""

@dataclass
class LifecyclePhase:
    """Phase in the safety lifecycle grouping related work products."""
    name: str
    work_products: List[SafetyWorkProduct] = field(default_factory=list)

@dataclass
class Workflow:
    """Named workflow consisting of sequential steps."""
    name: str
    steps: List[str] = field(default_factory=list)

@dataclass
class SafetyGovernance:
    """High level safety management model combining lifecycle and workflows."""
    phases: List[LifecyclePhase] = field(default_factory=list)
    workflows: List[Workflow] = field(default_factory=list)
