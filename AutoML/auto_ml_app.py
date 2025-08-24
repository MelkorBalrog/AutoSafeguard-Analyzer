from .core import *
class AutoMLApp:
    """Main application window for AutoML Analyzer."""
    _instance: Optional["AutoMLApp"] = None
    #: Maximum number of characters displayed for a notebook tab title. Longer
    #: titles are truncated with an ellipsis to avoid giant tabs that overflow
    #: the working area.
    MAX_TAB_TEXT_LENGTH = 20
    #: Maximum characters shown for tool notebook tab titles. Tool tabs use
    #: a fixed width so they remain readable but long names are capped at this
    #: length and truncated with an ellipsis.
    MAX_TOOL_TAB_TEXT_LENGTH = 20
    #: Maximum number of tabs displayed at once in the tools and document
    #: notebooks. Additional tabs can be accessed via the navigation buttons.
    MAX_VISIBLE_TABS = 4
    WORK_PRODUCT_INFO = {
        "Architecture Diagram": (
            "System Design (Item Definition)",
            "AutoML Explorer",
            "manage_architecture",
        "Safety & Security Concept": (
            "System Design (Item Definition)",
            "Safety & Security Case Explorer",
            "manage_safety_cases",
        "Safety & Security Case": (
            "Safety & Security Management",
            "Safety & Security Case Explorer",
            "manage_safety_cases",
        "GSN Argumentation": (
            "Safety & Security Management",
            "GSN Explorer",
            "manage_gsn",
        "GSN": (
            "Safety & Security Management",
            "GSN Explorer",
            "manage_gsn",
        "Requirement Specification": (
            "System Design (Item Definition)",
            "Requirements Editor",
            "show_requirements_editor",
        "Product Goal Specification": (
            "System Design (Item Definition)",
            "Product Goals Editor",
            "show_product_goals_editor",
        "HAZOP": (
            "Hazard & Threat Analysis",
            "HAZOP Analysis",
            "open_hazop_window",
        "STPA": (
            "Hazard & Threat Analysis",
            "STPA Analysis",
            "open_stpa_window",
        "Threat Analysis": (
            "Hazard & Threat Analysis",
            "Threat Analysis",
            "open_threat_window",
        "FI2TC": (
            "Hazard & Threat Analysis",
            "FI2TC Analysis",
            "open_fi2tc_window",
        "TC2FI": (
            "Hazard & Threat Analysis",
            "TC2FI Analysis",
            "open_tc2fi_window",
        "Risk Assessment": (
            "Risk Assessment",
            "Risk Assessment",
            "open_risk_assessment_window",
        "FMEA": (
            "Safety Analysis",
            "FMEA Manager",
            "show_fmea_list",
        "FMEDA": (
            "Safety Analysis",
            "FMEDA Manager",
            "show_fmeda_list",
        "Prototype Assurance Analysis": (
            "Safety Analysis",
            "Prototype Assurance Analysis",
            "create_paa_diagram",
        "FTA": (
            "Safety Analysis",
            "FTA Cut Sets",
            "show_cut_sets",
        "CTA": (
            "Safety Analysis",
            "CTA Diagrams",
            "create_cta_diagram",
        "Process": (
            "Process",
            "Calc Prototype Assurance Level (PAL)",
            "calculate_overall",
        "Qualitative Analysis": (
            "Hazard & Threat Analysis",
            "Hazard Explorer",
            "show_hazard_explorer",
        ),
        "Quantitative Analysis": (
            "Safety Analysis",
            "Reliability Analysis",
            "open_reliability_window",
        ),
        "Mission Profile": (
            "Safety Analysis",
            "Mission Profiles",
            "manage_mission_profiles",
        ),
        "Reliability Analysis": (
            "Safety Analysis",
            "Reliability Analysis",
            "open_reliability_window",
        ),
        "Causal Bayesian Network Analysis": (
            "Safety Analysis",
            "Causal Bayesian Network",
            "open_causal_bayesian_network_window",
        ),
        "Scenario Library": (
            "Scenario",
            "Scenario Libraries",
            "manage_scenario_libraries",
        ),
        "ODD": (
            "Scenario",
            "ODD Libraries",
            "manage_odd_libraries",
    for _wp in REQUIREMENT_WORK_PRODUCTS:
        WORK_PRODUCT_INFO.setdefault(
            _wp,
            (
                "System Design (Item Definition)",
                "Requirements Editor",
                "show_requirements_editor",
            ),
        )
    # Mapping of work products to their parent menu categories.  When a
    # child work product is enabled its parent menu must also become
    # active so the submenu is reachable.
    WORK_PRODUCT_PARENTS = {
        "HAZOP": "Risk Assessment",
        "Risk Assessment": None,
        "STPA": "Risk Assessment",
        "Threat Analysis": "Qualitative Analysis",
        "FI2TC": "Risk Assessment",
        "TC2FI": "Risk Assessment",
        "FMEA": "Qualitative Analysis",
        "Prototype Assurance Analysis": "Qualitative Analysis",
        "CTA": "Qualitative Analysis",
        "Product Goal Specification": "Requirements",
        "FMEDA": "Quantitative Analysis",
        "Mission Profile": "Quantitative Analysis",
        "Reliability Analysis": "Quantitative Analysis",
        "Causal Bayesian Network Analysis": "Quantitative Analysis",
        "FTA": "Quantitative Analysis",
        "Safety & Security Case": "GSN",
        "GSN Argumentation": "GSN",
        "ODD": "Scenario Library",
    }
    # Ensure all requirement work products activate the top-level Requirements
    # menu.  Each specific requirement specification (e.g. vehicle, functional
    # safety) is treated as a child of the generic "Requirements" category so
    # that declaring any of them on a governance diagram enables the
    # corresponding menu items.
    for _wp in REQUIREMENT_WORK_PRODUCTS:
        WORK_PRODUCT_PARENTS.setdefault(_wp, "Requirements")
    def __init__(self, root):
        AutoMLApp._instance = self
        self.root = root
        self.top_events = []
        self.cta_events = []
        self.paa_events = []
        self.fta_root_node = None
        self.cta_root_node = None
        self.paa_root_node = None
        self.analysis_tabs = {}
        self.shared_product_goals = {}
        self.selected_node = None
        self.clone_offset_counter = {}
        self._loaded_model_paths = []
        self.root.title("AutoML-Analyzer")
        self.version = VERSION
        self.zoom = 1.0
        self.rc_dragged = False
        self.diagram_font = tkFont.Font(family="Arial", size=int(8 * self.zoom))
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.style.configure(
            "Treeview",
            font=("Arial", 10),
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground="black",
            borderwidth=1,
            relief="sunken",
        )
        self.style.configure(
            "Treeview.Heading",
            background="#b5bdc9",
            foreground="black",
            relief="raised",
        )
        self.style.map(
            "Treeview.Heading",
            background=[("active", "#4a6ea9"), ("!active", "#b5bdc9")],
            foreground=[("active", "white"), ("!active", "black")],
        )
        # ------------------------------------------------------------------
        # Global color theme inspired by Windows classic / Windows 7
        # ------------------------------------------------------------------
        # Overall workspace background
        root.configure(background="#f0f0f0")
        # General widget colours
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", foreground="black")
        self.style.configure(
            "TEntry", fieldbackground="#ffffff", background="#ffffff", foreground="black"
        )
        self.style.configure(
            "TCombobox",
            fieldbackground="#ffffff",
            background="#ffffff",
            foreground="black",
        )
        self.style.configure(
            "TMenubutton", background="#e7edf5", foreground="black"
        )
        self.style.configure(
            "TScrollbar",
            background="#c0d4eb",
            troughcolor="#e2e6eb",
            bordercolor="#888888",
            arrowcolor="#555555",
            lightcolor="#eaf2fb",
            darkcolor="#5a6d84",
            borderwidth=2,
            relief="raised",
        )
        # Apply the scrollbar styling to both orientations
        for orient in ("Horizontal.TScrollbar", "Vertical.TScrollbar"):
            self.style.configure(orient,
                                background="#c0d4eb",
                                troughcolor="#e2e6eb",
                                bordercolor="#888888",
                                arrowcolor="#555555",
                                lightcolor="#eaf2fb",
                                darkcolor="#5a6d84",
                                borderwidth=2,
                                relief="raised")
        # Toolbox/LabelFrame titles
        self.style.configure(
            "Toolbox.TLabelframe",
            background="#fef9e7",
            bordercolor="#888888",
            lightcolor="#fffef7",
            darkcolor="#bfae6a",
            borderwidth=1,
            relief="raised",
        )
        self.style.configure(
            "Toolbox.TLabelframe.Label",
            background="#fef9e7",
            foreground="black",
            font=("Segoe UI", 10, "bold"),
            padding=(4, 0, 0, 0),
            anchor="w",
        )
        # Notebook (ribbon-like) title bars with beveled edges
        self.style.configure(
            "TNotebook",
            background="#c0d4eb",
            lightcolor="#eaf2fb",
            darkcolor="#5a6d84",
            borderwidth=2,
            relief="raised",
        )
        self.style.configure(
            "TNotebook.Tab",
            background="#b5bdc9",
            foreground="#555555",
            borderwidth=1,
            relief="raised",
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", "#4a6ea9"), ("!selected", "#b5bdc9")],
            foreground=[("selected", "white"), ("!selected", "#555555")],
        )
        # Closable notebook shares the same appearance
        self.style.configure(
            "ClosableNotebook",
            background="#c0d4eb",
            lightcolor="#eaf2fb",
            darkcolor="#5a6d84",
            borderwidth=2,
            relief="raised",
        )
        self.style.configure(
            "ClosableNotebook.Tab",
            background="#b5bdc9",
            foreground="#555555",
            borderwidth=1,
            relief="raised",
        )
        self.style.map(
            "ClosableNotebook.Tab",
            background=[("selected", "#4a6ea9"), ("!selected", "#b5bdc9")],
            foreground=[("selected", "white"), ("!selected", "#555555")],
        )
        # Mac-like capsule buttons
        def _build_pill(top: str, bottom: str) -> tk.PhotoImage:
            img = tk.PhotoImage(width=40, height=20)
            # ``PhotoImage.put`` only accepts RGB colors. Some Tk builds
            # (notably older Windows releases) mis-handle 8‑digit hex
            # values used for transparency and instead raise a
            # ``TclError``.  To keep the routine portable we fill the
            # image with a solid RGB color and, where supported, mark that
            # color as transparent.
            img.put("#000000", to=(0, 0, 40, 20))
            try:
                img.transparency_set(0, 0, 0)
            except Exception:
                pass
            radius = 10
            t_r = int(top[1:3], 16)
            t_g = int(top[3:5], 16)
            t_b = int(top[5:7], 16)
            b_r = int(bottom[1:3], 16)
            b_g = int(bottom[3:5], 16)
            b_b = int(bottom[5:7], 16)
            for y in range(20):
                ratio = y / 19
                r = int(t_r * (1 - ratio) + b_r * ratio)
                g = int(t_g * (1 - ratio) + b_g * ratio)
                b = int(t_b * (1 - ratio) + b_b * ratio)
                color = f"#{r:02x}{g:02x}{b:02x}"
                for x in range(40):
                    if x < radius:
                        if (x - radius) ** 2 + (y - radius) ** 2 <= radius ** 2:
                            img.put(color, (x, y))
                    elif x >= 40 - radius:
                        if (x - (40 - radius - 1)) ** 2 + (y - radius) ** 2 <= radius ** 2:
                            img.put(color, (x, y))
                    else:
                        img.put(color, (x, y))
            return img
        self._btn_imgs = {
            "normal": _build_pill("#fdfdfd", "#d2d2d2"),
            "active": _build_pill("#eaeaea", "#c8c8c8"),
            "pressed": _build_pill("#d0d0d0", "#a5a5a5"),
        }
        self.style.element_create(
            "RoundedButton",
            "image",
            self._btn_imgs["normal"],
            ("active", self._btn_imgs["active"]),
            ("pressed", self._btn_imgs["pressed"]),
            border=10,
            sticky="nsew",
        )
        self.style.map(
            "TButton",
            relief=[("pressed", "sunken"), ("!pressed", "raised")],
        )
        # Navigation buttons used to scroll document tabs
        self._init_nav_button_style()
        # Increase notebook tab font/size so titles are fully visible
        self.style.configure(
            "TNotebook.Tab", font=("Arial", 10), padding=(10, 5), width=20
        )
        self.style.configure(
            "ClosableNotebook.Tab", font=("Arial", 10), padding=(10, 5), width=20
        )
        # style-aware icons used across tree views
        style_mgr = StyleManager.get_instance()
        def _color(name: str, fallback: str = "black") -> str:
            c = style_mgr.get_color(name)
            return fallback if c == "#FFFFFF" else c
        self.pkg_icon = self._create_icon("folder", _color("Lifecycle Phase", "#b8860b"))
        self.gsn_module_icon = self.pkg_icon
        self.gsn_diagram_icon = self._create_icon("rect", "#4682b4")
        # small icons for diagram types shown in explorers
        self.diagram_icons = {
            "Use Case Diagram": self._create_icon("usecase_diag", _color("Use Case Diagram", "blue")),
            "Activity Diagram": self._create_icon("activity_diag", _color("Activity Diagram", "green")),
            "Governance Diagram": self._create_icon("activity_diag", _color("Governance Diagram", "green")),
            "Block Diagram": self._create_icon("block_diag", _color("Block Diagram", "orange")),
            "Internal Block Diagram": self._create_icon("ibd_diag", _color("Internal Block Diagram", "purple")),
            "Control Flow Diagram": self._create_icon("activity_diag", _color("Control Flow Diagram", "red")),
        }
        self.clipboard_node = None
        self.diagram_clipboard = None
        self.diagram_clipboard_type = None
        self.active_arch_window = None
        self.cut_mode = False
        self.page_history = []
        self.project_properties = {
            "pdf_report_name": "AutoML-Analyzer PDF Report",
            "pdf_detailed_formulas": True,
            "exposure_probabilities": EXPOSURE_PROBABILITIES.copy(),
            "controllability_probabilities": CONTROLLABILITY_PROBABILITIES.copy(),
            "severity_probabilities": SEVERITY_PROBABILITIES.copy(),
        }
        update_probability_tables(
            self.project_properties["exposure_probabilities"],
            self.project_properties["controllability_probabilities"],
            self.project_properties["severity_probabilities"],
        )
        self.item_definition = {"description": "", "assumptions": ""}
        self.safety_concept = {"functional": "", "technical": "", "cybersecurity": ""}
        self.mission_profiles = []
        self.fmeda_components = []
        self.reliability_analyses = []
        self.reliability_components = []
        self.reliability_total_fit = 0.0
        self.spfm = 0.0
        self.lpfm = 0.0
        self.reliability_dc = 0.0
        # Lists of user-defined faults and malfunctions
        self.faults: list[str] = []
        self.malfunctions: list[str] = []
        self.hazards: list[str] = []
        self.hazard_severity: dict[str, int] = {}
        self.failures: list[str] = []
        self.triggering_conditions: list[str] = []
        self.functional_insufficiencies: list[str] = []
        self.triggering_condition_nodes = []
        self.functional_insufficiency_nodes = []
        self.hazop_docs = []  # list of HazopDoc
        self.hara_docs = []   # list of HaraDoc
        self.stpa_docs = []   # list of StpaDoc
        self.threat_docs = []  # list of ThreatDoc
        self.active_hazop = None
        self.active_hara = None
        self.active_stpa = None
        self.active_threat = None
        self.hazop_entries = []  # backwards compatibility for active doc
        self.hara_entries = []
        self.stpa_entries = []
        self.threat_entries = []
        self.fi2tc_docs = []  # list of FI2TCDoc
        self.tc2fi_docs = []  # list of TC2FIDoc
        self.active_fi2tc = None
        self.active_tc2fi = None
        self.cbn_docs = []  # list of CausalBayesianNetworkDoc
        self.active_cbn = None
        self.cybersecurity_goals: list[CybersecurityGoal] = []
        self.arch_diagrams = []
        self.management_diagrams = []
        self.gsn_modules = []  # top-level GSN modules
        self.gsn_diagrams = []  # diagrams not assigned to a module
        # Track open diagram tabs to avoid duplicates
        self.diagram_tabs: dict[str, ttk.Frame] = {}
        self.top_events = []
        self.reviews = []
        self.review_data = None
        self.review_window = None
        self.safety_mgmt_toolbox = SafetyManagementToolbox()
        self.safety_mgmt_toolbox.on_change = self._on_toolbox_change
        self.current_user = ""
        self.comment_target = None
        self._undo_stack: list[dict] = []
        self._redo_stack: list[dict] = []
        # Track which work products are currently enabled. Menu entries for
        # these products remain disabled until the corresponding governance
        # diagram adds the work product. The mapping stores references to the
        # menu and entry index for each work product so they can be toggled at
        # runtime.
        self.enabled_work_products: set[str] = set()
        self.work_product_menus: dict[str, list[tuple[tk.Menu, int]]] = {}
        self.versions = []
        self.diff_nodes = []
        self.fi2tc_entries = []
        self.tc2fi_entries = []
        self.scenario_libraries = []
        self.odd_libraries = []
        self.odd_elements = []
        self.update_odd_elements()
        # Provide the drawing helper to dialogs that may be opened later
        self.fta_drawing_helper = fta_drawing_helper
        self.mechanism_libraries = []
        self.selected_mechanism_libraries = []
        self.fmedas = []  # list of FMEDA documents
        self.load_default_mechanisms()
        self.mechanism_libraries = []
        self.selected_mechanism_libraries = []
        self.fmedas = []  # list of FMEDA documents
        self.load_default_mechanisms()
        self.mechanism_libraries = []
        self.load_default_mechanisms()
        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New AutoML Model", command=self.new_model, accelerator="Ctrl+N")
        file_menu.add_command(label="Save AutoML Model", command=self.save_model, accelerator="Ctrl+S")
        file_menu.add_command(label="Load AutoML Model", command=self.load_model, accelerator="Ctrl+O")
        file_menu.add_command(label="Project Properties", command=self.edit_project_properties)
        file_menu.add_command(label="Save PDF Report", command=self.generate_pdf_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.confirm_close)
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Edit Selected", command=self.edit_selected)
        edit_menu.add_command(label="Remove Connection", command=lambda: self.remove_connection(self.selected_node) if self.selected_node else None)
        edit_menu.add_command(label="Delete Node", command=lambda: self.delete_node_and_subtree(self.selected_node) if self.selected_node else None)
        edit_menu.add_command(label="Remove Node", command=self.remove_node)
        edit_menu.add_separator()
        edit_menu.add_command(label="Copy", command=self.copy_node, accelerator="Ctrl+C")
        edit_menu.add_command(label="Cut", command=self.cut_node, accelerator="Ctrl+X")
        edit_menu.add_command(label="Paste", command=self.paste_node, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Edit User Name", command=self.edit_user_name, accelerator="Ctrl+U")
        edit_menu.add_command(label="Edit Description", command=self.edit_description, accelerator="Ctrl+D")
        edit_menu.add_command(label="Edit Rationale", command=self.edit_rationale, accelerator="Ctrl+L")
        edit_menu.add_command(label="Edit Value", command=self.edit_value)
        edit_menu.add_command(label="Edit Gate Type", command=self.edit_gate_type, accelerator="Ctrl+G")
        edit_menu.add_command(label="Edit Severity", command=self.edit_severity, accelerator="Ctrl+E")
        edit_menu.add_command(label="Edit Controllability", command=self.edit_controllability)
        edit_menu.add_command(label="Edit Page Flag", command=self.edit_page_flag)
        search_menu = tk.Menu(menubar, tearoff=0)
        search_menu.add_command(
            label="Find...", command=self.open_search_toolbox, accelerator="Ctrl+F"
        )
        process_menu = tk.Menu(menubar, tearoff=0)
        process_menu.add_command(label="Calc Prototype Assurance Level (PAL)", command=self.calculate_overall, accelerator="Ctrl+R")
        process_menu.add_command(label="Calc PMHF", command=self.calculate_pmfh, accelerator="Ctrl+M")
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Style Editor", command=self.open_style_editor)
        view_menu.add_command(
            label="Light Mode",
            command=lambda: self.apply_style('pastel.xml'),
        )
        view_menu.add_command(label="Metrics", command=self.open_metrics_tab)
        requirements_menu = tk.Menu(menubar, tearoff=0)
        requirements_menu.add_command(
            label="Requirements Matrix",
            command=self.show_requirements_matrix,
            state=tk.DISABLED,
        )
        matrix_idx = requirements_menu.index("end")
        requirements_menu.add_command(
            label="Requirements Editor",
            command=self.show_requirements_editor,
            state=tk.DISABLED,
        )
        editor_idx = requirements_menu.index("end")
        requirements_menu.add_command(
            label="Requirements Explorer",
            command=self.show_requirements_explorer,
            state=tk.DISABLED,
        )
        explorer_idx = requirements_menu.index("end")
        for wp in REQUIREMENT_WORK_PRODUCTS:
            self.work_product_menus.setdefault(wp, []).extend(
                [
                    (requirements_menu, matrix_idx),
                    (requirements_menu, editor_idx),
                    (requirements_menu, explorer_idx),
                ]
        requirements_menu.add_command(
            label="Product Goals Matrix", command=self.show_safety_goals_matrix
        requirements_menu.add_command(
            label="Product Goals Editor",
            command=self.show_product_goals_editor,
            state=tk.DISABLED,
        self.work_product_menus.setdefault("Product Goal Specification", []).append(
            (requirements_menu, requirements_menu.index("end"))
        requirements_menu.add_command(
            label="Safety Performance Indicators",
            command=self.show_safety_performance_indicators,
        self._add_lifecycle_requirements_menu(requirements_menu)
        self.phase_req_menu = tk.Menu(requirements_menu, tearoff=0)
        requirements_menu.add_cascade(
            label="Phase Requirements", menu=self.phase_req_menu
        self._refresh_phase_requirements_menu()
        requirements_menu.add_command(
            label="Export Product Goal Requirements",
            command=self.export_product_goal_requirements,
        review_menu = tk.Menu(menubar, tearoff=0)
        review_menu.add_command(label="Start Peer Review", command=self.start_peer_review)
        review_menu.add_command(label="Start Joint Review", command=self.start_joint_review)
        review_menu.add_command(label="Open Review Toolbox", command=self.open_review_toolbox)
        review_menu.add_command(label="Set Current User", command=self.set_current_user)
        review_menu.add_command(label="Merge Review Comments", command=self.merge_review_comments)
        review_menu.add_command(label="Compare Versions", command=self.compare_versions)
        architecture_menu = tk.Menu(menubar, tearoff=0)
        architecture_menu.add_command(label="Use Case Diagram", command=self.open_use_case_diagram)
        architecture_menu.add_command(label="Activity Diagram", command=self.open_activity_diagram)
        architecture_menu.add_command(label="Block Diagram", command=self.open_block_diagram)
        architecture_menu.add_command(label="Internal Block Diagram", command=self.open_internal_block_diagram)
        architecture_menu.add_command(label="Control Flow Diagram", command=self.open_control_flow_diagram)
        architecture_menu.add_separator()
        architecture_menu.add_command(
            label="AutoML Explorer",
            command=self.manage_architecture,
            state=tk.DISABLED,
        self.work_product_menus.setdefault("Architecture Diagram", []).append(
            (architecture_menu, architecture_menu.index("end"))
        # --- Risk Assessment Menu ---
        risk_menu = tk.Menu(menubar, tearoff=0)
        risk_menu.add_command(
            label="HAZOP Analysis",
            command=self.open_hazop_window,
            state=tk.DISABLED,
        self.work_product_menus.setdefault("HAZOP", []).append(
            (risk_menu, risk_menu.index("end"))
        risk_menu.add_command(
            label="Risk Assessment",
            command=self.open_risk_assessment_window,
            state=tk.DISABLED,
        self.work_product_menus.setdefault("Risk Assessment", []).append(
            (risk_menu, risk_menu.index("end"))
        risk_menu.add_command(
            label="STPA Analysis",
            command=self.open_stpa_window,
            state=tk.DISABLED,
        self.work_product_menus.setdefault("STPA", []).append(
            (risk_menu, risk_menu.index("end"))
        risk_menu.add_command(
            label="Threat Analysis",
            command=self.open_threat_window,
            state=tk.DISABLED,
        self.work_product_menus.setdefault("Threat Analysis", []).append(
            (risk_menu, risk_menu.index("end"))
        risk_menu.add_command(label="Hazard Explorer", command=self.show_hazard_explorer)
        risk_menu.add_command(label="Hazards Editor", command=self.show_hazard_editor)
        risk_menu.add_command(label="Malfunctions Editor", command=self.show_malfunction_editor)
        risk_menu.add_command(label="Triggering Conditions", command=self.show_triggering_condition_list)
        risk_menu.add_command(label="Functional Insufficiencies", command=self.show_functional_insufficiency_list)
        risk_menu.add_separator()
        risk_menu.add_command(
            label="FI2TC Analysis",
            command=self.open_fi2tc_window,
            state=tk.DISABLED,
        self.work_product_menus.setdefault("FI2TC", []).append(
            (risk_menu, risk_menu.index("end"))
        risk_menu.add_command(
            label="TC2FI Analysis",
            command=self.open_tc2fi_window,
            state=tk.DISABLED,
        self.work_product_menus.setdefault("TC2FI", []).append(
            (risk_menu, risk_menu.index("end"))
                
        # --- Qualitative Analysis Menu ---
        qualitative_menu = tk.Menu(menubar, tearoff=0)
        qualitative_menu.add_command(
            label="FMEA Manager",
            command=self.show_fmea_list,
            state=tk.DISABLED,
        self.work_product_menus.setdefault("FMEA", []).append(
            (qualitative_menu, qualitative_menu.index("end"))
        cta_menu = tk.Menu(qualitative_menu, tearoff=0)
        cta_menu.add_command(label="Add Top Level Event", command=self.create_cta_diagram)
        cta_menu.add_separator()
        cta_menu.add_command(label="Add Triggering Condition", command=lambda: self.add_node_of_type("Triggering Condition"))
        self._cta_menu_indices = {"add_trigger": cta_menu.index("end")}
        cta_menu.add_command(label="Add Functional Insufficiency", command=lambda: self.add_node_of_type("Functional Insufficiency"))
        self._cta_menu_indices["add_functional_insufficiency"] = cta_menu.index("end")
        qualitative_menu.add_cascade(label="CTA", menu=cta_menu, state=tk.DISABLED)
        self.work_product_menus.setdefault("CTA", []).append(
            (qualitative_menu, qualitative_menu.index("end"))
        self.cta_menu = cta_menu
        qualitative_menu.add_command(
            label="Fault Prioritization",
            command=self.open_fault_prioritization_window,

        paa_menu = tk.Menu(qualitative_menu, tearoff=0)
        paa_menu.add_command(label="Add Top Level Event", command=self.create_paa_diagram)
        paa_menu.add_separator()
        paa_menu.add_command(
            label="Add Confidence",
            command=lambda: self.add_node_of_type("Confidence Level"),
            accelerator="Ctrl+Shift+C",
        self._paa_menu_indices = {"add_confidence": paa_menu.index("end")}
        paa_menu.add_command(
            label="Add Robustness",
            command=lambda: self.add_node_of_type("Robustness Score"),
            accelerator="Ctrl+Shift+R",
        self._paa_menu_indices["add_robustness"] = paa_menu.index("end")
        qualitative_menu.add_cascade(
            label="Prototype Assurance Analysis",
            menu=paa_menu,
            state=tk.DISABLED,
        self.work_product_menus.setdefault("Prototype Assurance Analysis", []).append(
            (qualitative_menu, qualitative_menu.index("end"))
        self.paa_menu = paa_menu
        
        # --- Quantitative Analysis Menu ---
        quantitative_menu = tk.Menu(menubar, tearoff=0)
        quantitative_menu.add_command(
            label="Mission Profiles",
            command=self.manage_mission_profiles,
        self.work_product_menus.setdefault("Mission Profile", []).append(
            (quantitative_menu, quantitative_menu.index("end"))
                
        quantitative_menu.add_separator()
        quantitative_menu.add_command(label="Faults Editor", command=self.show_fault_editor)
        quantitative_menu.add_command(label="Failures Editor", command=self.show_failure_editor)
        quantitative_menu.add_separator()
        
        quantitative_menu.add_command(
            label="Mechanism Libraries", command=self.manage_mechanism_libraries
        )
        quantitative_menu.add_command(
            label="Reliability Analysis",
            command=self.open_reliability_window,
        self.work_product_menus.setdefault("Reliability Analysis", []).append(
            (quantitative_menu, quantitative_menu.index("end"))
        quantitative_menu.add_command(
            label="Causal Bayesian Network",
            command=self.open_causal_bayesian_network_window,
        self.work_product_menus.setdefault("Causal Bayesian Network Analysis", []).append(
            (quantitative_menu, quantitative_menu.index("end"))
        quantitative_menu.add_command(
            label="FMEDA Analysis",
            command=self.open_fmeda_window,
            state=tk.DISABLED,
        self.work_product_menus.setdefault("FMEDA", []).append(
            (quantitative_menu, quantitative_menu.index("end"))
        quantitative_menu.add_command(
            label="FMEDA Manager",
            command=self.show_fmeda_list,
        fta_menu = tk.Menu(quantitative_menu, tearoff=0)
        fta_menu.add_command(label="Add Top Level Event", command=self.create_fta_diagram)
        fta_menu.add_separator()
        fta_menu.add_command(label="Add Gate", command=lambda: self.add_node_of_type("GATE"), accelerator="Ctrl+Shift+G")
        self._fta_menu_indices = {"add_gate": fta_menu.index("end")}
        fta_menu.add_command(label="Add Basic Event", command=lambda: self.add_node_of_type("Basic Event"), accelerator="Ctrl+Shift+B")
        self._fta_menu_indices["add_basic_event"] = fta_menu.index("end")
        fta_menu.add_command(label="Add FMEA/FMEDA Event", command=self.add_basic_event_from_fmea)
        fta_menu.add_command(label="Add Gate from Failure Mode", command=self.add_gate_from_failure_mode)
        self._fta_menu_indices["add_gate_from_failure_mode"] = fta_menu.index("end")
        fta_menu.add_command(label="Add Fault Event", command=self.add_fault_event)
        self._fta_menu_indices["add_fault_event"] = fta_menu.index("end")
        fta_menu.add_separator()
        fta_menu.add_command(label="FTA-FMEA Traceability", command=self.show_traceability_matrix)
        fta_menu.add_command(
            label="FTA Cut Sets",
            command=self.show_cut_sets,
        fta_menu.add_command(label="Common Cause Toolbox", command=self.show_common_cause_view)
        fta_menu.add_command(label="Cause & Effect Chain", command=self.show_cause_effect_chain)
        self.fta_menu = fta_menu
        quantitative_menu.add_cascade(label="FTA", menu=fta_menu, state=tk.DISABLED)
        self.work_product_menus.setdefault("FTA", []).append(
            (quantitative_menu, quantitative_menu.index("end"))
        
        libs_menu = tk.Menu(menubar, tearoff=0)
        libs_menu.add_command(
            label="Scenario Libraries",
            command=self.manage_scenario_libraries,

        self.update_hara_statuses()
        self.update_fta_statuses()
        self.versions = data.get("versions", [])

        self.selected_node = None
        if hasattr(self, "page_diagram") and self.page_diagram is not None:
            self.close_page_diagram()
            self.apply_governance_rules()
        except Exception:
            pass
        self.update_views()

    def save_model(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".autml",
            filetypes=[("AutoML Project", "*.autml"), ("JSON", "*.json")],
        )
        if not path:
            return
        try:
            from cryptography.fernet import Fernet
        except Exception:  # pragma: no cover - dependency check
            import subprocess
            import sys

            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "cryptography"]
                )
                from cryptography.fernet import Fernet
            except Exception:
                messagebox.showerror(
                    "Save Model", "cryptography package is required for encrypted save."
                )
                return
        import base64
        import gzip
        import hashlib
        import json
        import os

        for fmea in self.fmeas:
            self.export_fmea_to_csv(fmea, fmea["file"])
        for fmeda in self.fmedas:
            self.export_fmeda_to_csv(fmeda, fmeda["file"])
        data = self.export_model_data()

        if path.endswith(".autml"):
            try:
                from cryptography.fernet import Fernet
            except Exception:  # pragma: no cover - dependency check
                messagebox.showwarning(
                    "Save Model",
                    (
                        "cryptography package is required for encrypted save. "
                        "Saving unencrypted JSON instead."
                    ),
                )
                path = os.path.splitext(path)[0] + ".json"
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                import base64
                import gzip
                import hashlib

                password = askstring_fixed(
                    simpledialog,
                    "Password",
                    "Enter encryption password:",
                    show="*",
                )
                if password is None:
                    return
                raw = json.dumps(data).encode("utf-8")
                compressed = gzip.compress(raw)
                key = base64.urlsafe_b64encode(
                    hashlib.sha256(password.encode()).digest()
                )
                token = Fernet(key).encrypt(compressed)
                with open(path, "wb") as f:
                    f.write(token)
        else:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        messagebox.showinfo(
            "Saved", "Model saved with all configuration and safety goal information."
        )
        self.set_last_saved_state()

    def _reset_on_load(self):
        """Close all open windows and clear state before loading a project."""

        if getattr(self, "page_diagram", None) is not None:
            self.close_page_diagram()

        for tab_id in list(getattr(self.doc_nb, "tabs", lambda: [])()):
            self.doc_nb._closing_tab = tab_id
            self.doc_nb.event_generate("<<NotebookTabClosed>>")
            if tab_id in getattr(self.doc_nb, "tabs", lambda: [])():
                try:
                    self.doc_nb.forget(tab_id)
                except Exception:
                    pass

        for win in (
            list(getattr(self, "use_case_windows", []))
            + list(getattr(self, "activity_windows", []))
            + list(getattr(self, "block_windows", []))
            + list(getattr(self, "ibd_windows", []))
        ):
            try:
                win.destroy()
            except Exception:
                pass
        self.use_case_windows = []
        self.activity_windows = []
        self.block_windows = []
        self.ibd_windows = []

        global AutoML_Helper, unique_node_id_counter
        SysMLRepository.reset_instance()
        AutoML_Helper = AutoMLHelper()
        unique_node_id_counter = 1

        self.top_events = []
        self.cta_events = []
        self.root_node = None
        self.selected_node = None
        self.page_history = []
        self._undo_stack.clear()
        self._redo_stack.clear()
        if getattr(self, "analysis_tree", None):
            self.analysis_tree.delete(*self.analysis_tree.get_children())

        self._reset_fta_state()

    def _prompt_save_before_load_v1(self):
        return messagebox.askyesnocancel(
            "Load Model", "Save current project before loading?"
        )

    def _prompt_save_before_load_v2(self):
        return messagebox.askyesnocancel(
            "Load Model", "Would you like to save before loading a new project?"
        )

    def _prompt_save_before_load_v3(self):
        message = "You have unsaved changes. Save before loading a project?"
        return messagebox.askyesnocancel("Load Model", message)

    def _prompt_save_before_load_v4(self):
        opts = {
            "title": "Load Model",
            "message": "Save changes before loading another project?",
        }
        return messagebox.askyesnocancel(**opts)

    def _prompt_save_before_load(self):
        return self._prompt_save_before_load_v3()

    def load_model(self):
        import json

        if getattr(self, "has_unsaved_changes", lambda: False)():
            resp = self._prompt_save_before_load()
            if resp is None:
                return
            if resp:
                self.save_model()
        path = filedialog.askopenfilename(
            defaultextension=".autml",
            filetypes=[("AutoML Project", "*.autml"), ("JSON", "*.json")],
        )
        if not path:
            return
        if path.endswith(".autml"):
            try:
                from cryptography.fernet import Fernet, InvalidToken
            except Exception:  # pragma: no cover - dependency check
                import subprocess
                import sys

                try:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", "cryptography"]
                    )
                    from cryptography.fernet import Fernet, InvalidToken
                except Exception:
                    messagebox.showerror(
                        "Load Model", "cryptography package is required for encrypted files."
                    )
                    return
            import base64
            import gzip
            import hashlib
            import json

            password = askstring_fixed(
                simpledialog,
                "Password",
                "Enter decryption password:",
                show="*",
            if password is None:
                return
            key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
            with open(path, "rb") as f:
                token = f.read()
            try:
                compressed = Fernet(key).decrypt(token)
            except InvalidToken:
                messagebox.showerror("Load Model", "Decryption failed. Check password.")
                return
            try:
                raw = gzip.decompress(compressed).decode("utf-8")
                data = json.loads(raw)
            except Exception as exc:  # pragma: no cover - parsing failure
                messagebox.showerror("Load Model", f"Failed to parse model: {exc}")
                return
        else:
            with open(path, "r") as f:
                raw = f.read()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                import re

                def clean(text: str) -> str:
                    text = re.sub(r"//.*", "", text)
                    text = re.sub(r"#.*", "", text)
                    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
                    text = re.sub(r",\s*(\]|\})", r"\1", text)
                    return text
                try:
                    data = json.loads(clean(raw))
                except json.JSONDecodeError:
                    messagebox.showerror(
                        "Load Model", f"Failed to parse JSON file:\n{exc}"
                    )
                    return
        self._reset_on_load()
        self.apply_model_data(data)
        self.set_last_saved_state()
        self._loaded_model_paths.append(path)
        return
    def _reregister_document(self, analysis: str, name: str) -> None:
        phase = self.safety_mgmt_toolbox.doc_phases.get(analysis, {}).get(name)
        current = self.safety_mgmt_toolbox.active_module
        try:
            self.safety_mgmt_toolbox.active_module = phase
            self.safety_mgmt_toolbox.register_created_work_product(analysis, name)
        finally:
            self.safety_mgmt_toolbox.active_module = current
    def update_global_requirements_from_nodes(self,node):
        if hasattr(node, "safety_requirements"):
            for req in node.safety_requirements:
                # Use req["id"] as key; if already exists, you could update if needed.
                ensure_requirement_defaults(req)
                if req["id"] not in global_requirements:
                    global_requirements[req["id"]] = req
                else:
                    ensure_requirement_defaults(global_requirements[req["id"]])
        for child in node.children:
            self.update_global_requirements_from_nodes(child)
    def generate_report(self):
        path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML", "*.html")])
        if path:
            html = self.build_html_report()
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            messagebox.showinfo("Report", "HTML report generated.")

    def build_html_report(self):
        def node_to_html(n):
            txt = f"{n.name} ({n.node_type}"
            if n.node_type.upper() in GATE_NODE_TYPES:
                txt += f", {n.gate_type}"
            txt += ")"
            if n.display_label:
                txt += f" => {n.display_label}"
            if n.description:
                txt += f"<br>Desc: {n.description}"
            if n.rationale:
                txt += f"<br>Rationale: {n.rationale}"
            content = f"<details open><summary>{txt}</summary>\n"
            for c in n.children:
                content += node_to_html(c)
            content += "</details>\n"
            return content
        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>AutoML-Analyzer</title>
<style>body {{ font-family: Arial; }} details {{ margin-left: 20px; }}</style>
</head>
<body>
<h1>AutoML-Analyzer</h1>
{node_to_html(self.root_node)}
</body>
</html>"""
    def resolve_original(self,node):
        # Walk the clone chain until you find a primary instance.
        while not node.is_primary_instance and node.original is not None and node.original != node:
            node = node.original
        return node
    def open_page_diagram(self, node, push_history=True):
        self.ensure_fta_tab()
        # Resolve the node to its original.
        resolved_node = self.resolve_original(node)
        if push_history and hasattr(self, "page_diagram") and self.page_diagram is not None:
            self.page_history.append(self.page_diagram.root_node)
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        # Create header frame with the original node’s name.
        header_frame = ttk.Frame(self.canvas_frame)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.columnconfigure(0, weight=1)
        header = tk.Label(header_frame, text=f"Page Diagram: {resolved_node.name}",
                          font=("Arial", 14, "bold"))
        header.grid(row=0, column=0, sticky="w", padx=(5, 0))
        back_button = ttk.Button(header_frame, text="Go Back", command=self.go_back)
        back_button.grid(row=0, column=1, sticky="e", padx=5)
        page_canvas = tk.Canvas(self.canvas_frame, bg=StyleManager.get_instance().canvas_bg)
        page_canvas.grid(row=1, column=0, sticky="nsew")
        page_canvas.diagram_mode = getattr(self, "diagram_mode", "FTA")
        vbar = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=page_canvas.yview)
        vbar.grid(row=1, column=1, sticky="ns")
        hbar = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=page_canvas.xview)
        hbar.grid(row=2, column=0, sticky="ew")
        page_canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.page_canvas = page_canvas
        self.canvas_frame.rowconfigure(0, weight=0)
        self.canvas_frame.rowconfigure(1, weight=1)
        self.canvas_frame.rowconfigure(2, weight=0)
        self.canvas_frame.columnconfigure(0, weight=1)
        # Use the resolved (original) node for the page diagram.
        self.page_diagram = PageDiagram(self, resolved_node, page_canvas)
        self.page_diagram.redraw_canvas()
        self.refresh_all()
    def go_back(self):
        if self.page_history:
            # Pop one page off the history and open it without pushing the current page again.
            previous_page = self.page_history.pop()
            self.open_page_diagram(previous_page, push_history=False)
        #else:
            # If history is empty, remain on the current (root) page.
            #messagebox.showinfo("Back", "You are already at the root page.")

    def draw_page_subtree(self, page_root):
        self.page_canvas.delete("all")
        self.draw_page_grid()
        visited_ids = set()
        self.draw_page_connections_subtree(page_root, visited_ids)
        self.draw_page_nodes_subtree(page_root)
        bbox = self.page_canvas.bbox("all")
        if bbox:
            self.page_canvas.config(scrollregion=bbox)

    def draw_page_grid(self):
        spacing = 20
        width = self.page_canvas.winfo_width() or 800
        height = self.page_canvas.winfo_height() or 600
        for x in range(0, width, spacing):
            self.page_canvas.create_line(x, 0, x, height, fill="#ddd", tags="grid")
        for y in range(0, height, spacing):
            self.page_canvas.create_line(0, y, width, y, fill="#ddd", tags="grid")

    def draw_page_connections_subtree(self, node, visited_ids):
        if id(node) in visited_ids:
        visited_ids.add(id(node))
        region_width = 100
        parent_bottom = (node.x, node.y + 40)
        N = len(node.children)
        for i, child in enumerate(node.children):
            parent_conn = (node.x - region_width/2 + (i+0.5)*(region_width/N), parent_bottom[1])
            child_top = (child.x, child.y - 45)
            draw_90_connection(self.page_canvas, parent_conn, child_top, outline_color="dimgray", line_width=1)
        for child in node.children:
            self.draw_page_connections_subtree(child, visited_ids)
    def draw_page_nodes_subtree(self, node):
        self.draw_node_on_page_canvas(node)
        for child in node.children:
            self.draw_page_nodes_subtree(child)
    def draw_node_on_page_canvas(self, canvas, node):
        # Use the clone's own display label and append a marker
        if not node.is_primary_instance:
            display_label = node.display_label + " (clone)"
        else:
            display_label = node.display_label
        
        fill_color = self.get_node_fill_color(node, getattr(canvas, "diagram_mode", None))
        eff_x, eff_y = node.x, node.y
        top_text = f"Type: {node.node_type}"
        if node.input_subtype:
            top_text += f" ({node.input_subtype})"
        if node.description:
            top_text += f"\nDesc: {node.description}"
        if node.rationale:
            top_text += f"\nRationale: {node.rationale}"
        bottom_text = node.name
        outline_color = "dimgray"
        line_width = 1
        if node.unique_id in getattr(self.app, "diff_nodes", []):
            outline_color = "blue"
            line_width = 2
        elif not node.is_primary_instance:
            outline_color = "red"
        
        # For page elements, assume they use a triangle shape.
        if node.is_page:
            fta_drawing_helper.draw_triangle_shape(
                canvas,
                eff_x,
                eff_y,
                scale=40,
                top_text=top_text,
                bottom_text=bottom_text,
                fill=fill_color,
                outline_color=outline_color,
                line_width=line_width,
                font_obj=self.diagram_font,
                obj_id=node.unique_id,
            )
        else:
            node_type_upper = node.node_type.upper()
            if node_type_upper in GATE_NODE_TYPES:
                if node.gate_type and node.gate_type.upper() == "OR":
                    fta_drawing_helper.draw_rotated_or_gate_shape(
                        self.page_canvas,
                        eff_x,
                        eff_y,
                        scale=40,
                        top_text=top_text,
                        bottom_text=bottom_text,
                        fill=fill_color,
                        outline_color=outline_color,
                        line_width=line_width,
                        obj_id=node.unique_id,
                    )
                else:
                    fta_drawing_helper.draw_rotated_and_gate_shape(
                        self.page_canvas,
                        eff_x,
                        eff_y,
                        scale=40,
                        top_text=top_text,
                        bottom_text=bottom_text,
                        fill=fill_color,
                        outline_color=outline_color,
                        line_width=line_width,
                        obj_id=node.unique_id,
                    )
            elif node_type_upper in ["CONFIDENCE LEVEL", "ROBUSTNESS SCORE"]:
                fta_drawing_helper.draw_circle_event_shape(
                    self.page_canvas,
                    eff_x,
                    eff_y,
                    45,
                    top_text=top_text,
                    bottom_text=bottom_text,
                    fill=fill_color,
                    outline_color=outline_color,
                    line_width=line_width,
                    obj_id=node.unique_id,
                )
            else:
                fta_drawing_helper.draw_circle_event_shape(
                    self.page_canvas,
                    eff_x,
                    eff_y,
                    45,
                    top_text=top_text,
                    bottom_text=bottom_text,
                    fill=fill_color,
                    outline_color=outline_color,
                    line_width=line_width,
                    obj_id=node.unique_id,
                )
        if self.review_data:
            unresolved = any(
                c.node_id == node.unique_id and not c.resolved
                for c in self.review_data.comments
            )
            if unresolved:
                canvas.create_oval(
                    eff_x + 35,
                    eff_y + 35,
                    eff_x + 45,
                    eff_y + 45,
                    fill="yellow",
                    outline=StyleManager.get_instance().outline_color,
                )
    def on_ctrl_mousewheel_page(self, event):
        if event.delta > 0:
            self.page_diagram.zoom_in()
        else:
            self.page_diagram.zoom_out()
    def close_page_diagram(self):
        if self.page_history:
            prev = self.page_history.pop()
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()
            if prev is None:
                self.canvas = tk.Canvas(self.canvas_frame, bg=StyleManager.get_instance().canvas_bg)
                self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                self.hbar = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
                self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
                self.vbar = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
                self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
                self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set,
                                   scrollregion=(0, 0, 2000, 2000))
                self.canvas.bind("<ButtonPress-3>", self.on_right_mouse_press)
                self.canvas.bind("<B3-Motion>", self.on_right_mouse_drag)
                self.canvas.bind("<Button-1>", self.on_canvas_click)
                self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
                self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
                self.canvas.bind("<Double-Button-1>", self.on_canvas_double_click)
                self.canvas.bind("<ButtonRelease-3>", self.on_right_mouse_release)
                self.update_views()
                self.page_diagram = None
            else:
                self.open_page_diagram(prev)
        else:
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()
            self.canvas = tk.Canvas(self.canvas_frame, bg=StyleManager.get_instance().canvas_bg)
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.hbar = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
            self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
            self.vbar = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
            self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set,
                               scrollregion=(0, 0, 2000, 2000))
            self.canvas.bind("<ButtonPress-3>", self.on_right_mouse_press)
            self.canvas.bind("<B3-Motion>", self.on_right_mouse_drag)
            self.canvas.bind("<Button-1>", self.on_canvas_click)
            self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
            self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
            self.canvas.bind("<Double-Button-1>", self.on_canvas_double_click)
            self.canvas.bind("<ButtonRelease-3>", self.on_right_mouse_release)
            self.update_views()
            self.page_diagram = None
    # --- Review Toolbox Methods ---
    def start_peer_review(self):
        dialog = ParticipantDialog(self.root, joint=False)
        if dialog.result:
            moderators, parts = dialog.result
            name = simpledialog.askstring("Review Name", "Enter unique review name:")
            if not name:
                return
            description = askstring_fixed(
                simpledialog,
                "Description",
                "Enter a short description:",
            )
            if description is None:
                description = ""
            if not moderators:
                messagebox.showerror("Review", "Please specify a moderator")
                return
            if not parts:
                messagebox.showerror("Review", "At least one reviewer required")
                return
            due_date = simpledialog.askstring("Due Date", "Enter due date (YYYY-MM-DD):")
            if any(r.name == name for r in self.reviews):
                messagebox.showerror("Review", "Name already exists")
                return
            scope = ReviewScopeDialog(self.root, self)
            (
                fta_ids,
                fmea_names,
                fmeda_names,
                hazop_names,
                hara_names,
                stpa_names,
                fi2tc_names,
                tc2fi_names,
            ) = scope.result if scope.result else ([], [], [], [], [], [], [], [])
            review = ReviewData(
                name=name,
                description=description,
                mode='peer',
                moderators=moderators,
                participants=parts,
                comments=[],
                fta_ids=fta_ids,
                fmea_names=fmea_names,
                fmeda_names=fmeda_names,
                hazop_names=hazop_names,
                hara_names=hara_names,
                stpa_names=stpa_names,
                fi2tc_names=fi2tc_names,
                tc2fi_names=tc2fi_names,
                due_date=due_date,
            )
            self.reviews.append(review)
            self.review_data = review
            self.current_user = moderators[0].name if moderators else parts[0].name
            self.open_review_document(review)
            self.send_review_email(review)
            self.open_review_toolbox()
    def start_joint_review(self):
        dialog = ParticipantDialog(self.root, joint=True)
        if dialog.result:
            moderators, participants = dialog.result
            name = simpledialog.askstring("Review Name", "Enter unique review name:")
            if not name:
                return
            description = askstring_fixed(
                simpledialog,
                "Description",
                "Enter a short description:",
            )
            if description is None:
                description = ""
            if not moderators:
                messagebox.showerror("Review", "Please specify a moderator")
                return
            if not any(p.role == 'reviewer' for p in participants):
                messagebox.showerror("Review", "At least one reviewer required")
                return
            if not any(p.role == 'approver' for p in participants):
                messagebox.showerror("Review", "At least one approver required")
                return
            due_date = simpledialog.askstring("Due Date", "Enter due date (YYYY-MM-DD):")
            if any(r.name == name for r in self.reviews):
                messagebox.showerror("Review", "Name already exists")
                return
            scope = ReviewScopeDialog(self.root, self)
            (
                fta_ids,
                fmea_names,
                fmeda_names,
                hazop_names,
                hara_names,
                stpa_names,
                fi2tc_names,
                tc2fi_names,
            ) = scope.result if scope.result else ([], [], [], [], [], [], [], [])
            # Ensure each selected element has a completed peer review
            def peer_completed(pred):
                return any(
                    r.mode == 'peer'
                    and getattr(r, 'reviewed', False)
                    and pred(r)
                    for r in self.reviews
            for tid in fta_ids:
                if not peer_completed(lambda r: tid in r.fta_ids):
                    messagebox.showerror(
                        "Review",
                        "Peer review must be reviewed before starting joint review",
                    )
                    return
            for name_fta in fmea_names:
                if not peer_completed(lambda r: name_fta in r.fmea_names):
                    messagebox.showerror(
                        "Review",
                        "Peer review must be reviewed before starting joint review",
                    )
                    return
            for name_fd in fmeda_names:
                if not peer_completed(lambda r: name_fd in r.fmeda_names):
                    messagebox.showerror(
                        "Review",
                        "Peer review must be reviewed before starting joint review",
                    )
                    return
            for name_hz in hazop_names:
                if not peer_completed(lambda r: name_hz in getattr(r, 'hazop_names', [])):
                    messagebox.showerror(
                        "Review",
                        "Peer review must be reviewed before starting joint review",
                    )
                    return
            for name_hara in hara_names:
                if not peer_completed(lambda r: name_hara in getattr(r, 'hara_names', [])):
                    messagebox.showerror(
                        "Review",
                        "Peer review must be reviewed before starting joint review",
                    )
                    return
            for name_stpa in stpa_names:
                if not peer_completed(lambda r: name_stpa in getattr(r, 'stpa_names', [])):
                    messagebox.showerror(
                        "Review",
                        "Peer review must be reviewed before starting joint review",
                    )
                    return
            for name_fi in fi2tc_names:
                if not peer_completed(lambda r: name_fi in getattr(r, 'fi2tc_names', [])):
                    messagebox.showerror(
                        "Review",
                        "Peer review must be reviewed before starting joint review",
                    )
                    return
            for name_tc in tc2fi_names:
                if not peer_completed(lambda r: name_tc in getattr(r, 'tc2fi_names', [])):
                    messagebox.showerror(
                        "Review",
                        "Peer review must be reviewed before starting joint review",
                    )
                    return
            review = ReviewData(
                name=name,
                description=description,
                mode='joint',
                moderators=moderators,
                participants=participants,
                comments=[],
                fta_ids=fta_ids,
                fmea_names=fmea_names,
                fmeda_names=fmeda_names,
                hazop_names=hazop_names,
                hara_names=hara_names,
                stpa_names=stpa_names,
                fi2tc_names=fi2tc_names,
                tc2fi_names=tc2fi_names,
                due_date=due_date,
            )
            self.reviews.append(review)
            self.review_data = review
            self.current_user = moderators[0].name if moderators else participants[0].name
            self.open_review_document(review)
            self.send_review_email(review)
            self.open_review_toolbox()
    def open_review_document(self, review):
        if hasattr(self, "_review_doc_tab") and self._review_doc_tab.winfo_exists():
            self.doc_nb.select(self._review_doc_tab)
        else:
            title = f"Review {review.name}"
            self._review_doc_tab = self._new_tab(title)
            self._review_doc_window = ReviewDocumentDialog(self._review_doc_tab, self, review)
            self._review_doc_window.pack(fill=tk.BOTH, expand=True)
        self.refresh_all()
    def open_review_toolbox(self):
        if not self.reviews:
            messagebox.showwarning("Review", "No reviews defined")
        if not self.review_data and self.reviews:
            self.review_data = self.reviews[0]
        self.update_hara_statuses()
        self.update_fta_statuses()
        self.update_requirement_statuses()
        if hasattr(self, "_review_tab") and self._review_tab.winfo_exists():
            self.doc_nb.select(self._review_tab)
        else:
            self._review_tab = self._new_tab("Review")
            self.review_window = ReviewToolbox(self._review_tab, self)
            self.review_window.pack(fill=tk.BOTH, expand=True)
        self.refresh_all()
        self.set_current_user()

    def send_review_email(self, review):
        """Send the review summary to all reviewers via configured SMTP."""
        recipients = [p.email for p in review.participants if p.role == 'reviewer' and p.email]
        if not recipients:

        # Determine the current user's email if available
        current_email = next((p.email for p in review.participants
                              if p.name == self.current_user), "")

        if not getattr(self, "email_config", None):
            cfg = EmailConfigDialog(self.root, default_email=current_email).result
            self.email_config = cfg

        cfg = getattr(self, "email_config", None)
        if not cfg:
        subject = f"Review: {review.name}"
        lines = [f"Review Name: {review.name}", f"Description: {review.description}", ""]
        if review.fta_ids:
            lines.append("FTAs:")
            for tid in review.fta_ids:
                te = next((t for t in self.top_events if t.unique_id == tid), None)
                if te:
                    lines.append(f" - {te.name}")
            lines.append("")
        if review.fmea_names:
            lines.append("FMEAs:")
            for name in review.fmea_names:
                lines.append(f" - {name}")
            lines.append("")
        if getattr(review, 'hazop_names', []):
            lines.append("HAZOPs:")
            for name in review.hazop_names:
                lines.append(f" - {name}")
            lines.append("")
        if getattr(review, 'hara_names', []):
            lines.append("Risk Assessments:")
            for name in review.hara_names:
                lines.append(f" - {name}")
            lines.append("")
        content = "\n".join(lines)
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = cfg['email']
        msg['To'] = ', '.join(recipients)
        msg.set_content(content)
        html_lines = ["<html><body>", "<pre>", html.escape(content), "</pre>"]
        image_cids = []
        images = []
        for tid in review.fta_ids:
            node = self.find_node_by_id_all(tid)
            if not node:
                continue
            img = self.capture_diff_diagram(node)
            if img is None:
                continue
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            cid = make_msgid()
            label = node.user_name or node.name or f"id{tid}"
            html_lines.append(f"<p><b>FTA: {html.escape(label)}</b><br>" +
                             f"<img src=\"cid:{cid[1:-1]}\" alt=\"{html.escape(label)}\"></p>")
            image_cids.append(cid)
            images.append(buf.getvalue())
        diff_html = self.build_requirement_diff_html(review)
        if diff_html:
            html_lines.append("<b>Requirements:</b><br>" + diff_html)
        html_lines.append("</body></html>")
        html_body = "\n".join(html_lines)
        msg.add_alternative(html_body, subtype="html")
        html_part = msg.get_payload()[1]
        for cid, data in zip(image_cids, images):
            html_part.add_related(data, "image", "png", cid=cid)

        # Attach FMEA tables as CSV files (can be opened with Excel)
        for name in review.fmea_names:
            fmea = next((f for f in self.fmeas if f["name"] == name), None)
            if not fmea:
                continue
            out = StringIO()
            writer = csv.writer(out)
            columns = [
                "Component",
                "Parent",
                "Failure Mode",
                "Failure Effect",
                "Cause",
                "S",
                "O",
                "D",
                "RPN",
                "Requirements",
            ]
            writer.writerow(columns)
            for be in fmea["entries"]:
                src = self.get_failure_mode_node(be)
                comp = self.get_component_name_for_node(src) or "N/A"
                parent = src.parents[0] if src.parents else None
                parent_name = parent.user_name if parent and getattr(parent, "node_type", "").upper() not in GATE_NODE_TYPES else ""
                req_ids = "; ".join(
                    [f"{req['req_type']}:{req['text']}" for req in getattr(be, 'safety_requirements', [])]
                )
                rpn = be.fmea_severity * be.fmea_occurrence * be.fmea_detection
                failure_mode = be.description or (be.user_name or f"BE {be.unique_id}")
                row = [
                    comp,
                    parent_name,
                    failure_mode,
                    be.fmea_effect,
                    getattr(be, "fmea_cause", ""),
                    be.fmea_severity,
                    be.fmea_occurrence,
                    be.fmea_detection,
                    rpn,
                    req_ids,
                ]
                writer.writerow(row)
            csv_bytes = out.getvalue().encode('utf-8')
            out.close()
            msg.add_attachment(
                csv_bytes,
                maintype="text",
                subtype="csv",
                filename=f"fmea_{name}.csv",
            )
        for name in getattr(review, 'fmeda_names', []):
            fmeda = next((f for f in self.fmedas if f["name"] == name), None)
            if not fmeda:
                continue
            out = StringIO()
            writer = csv.writer(out)
            columns = [
                "Component","Parent","Failure Mode","Malfunction","Safety Goal","FaultType","Fraction","FIT","DiagCov","Mechanism"
            ]
            writer.writerow(columns)
            for be in fmeda["entries"]:
                src = self.get_failure_mode_node(be)
                comp = self.get_component_name_for_node(src) or "N/A"
                parent = src.parents[0] if src.parents else None
                parent_name = parent.user_name if parent and getattr(parent, "node_type", "").upper() not in GATE_NODE_TYPES else ""
                row = [
                    comp,
                    parent_name,
                    be.description or (be.user_name or f"BE {be.unique_id}"),
                    be.fmeda_malfunction,
                    be.fmeda_safety_goal,
                    be.fmeda_fault_type,
                    f"{be.fmeda_fault_fraction:.2f}",
                    f"{be.fmeda_fit:.2f}",
                    f"{be.fmeda_diag_cov:.2f}",
                    getattr(be, "fmeda_mechanism", ""),
                ]
                writer.writerow(row)
            csv_bytes = out.getvalue().encode('utf-8')
            out.close()
            msg.add_attachment(
                csv_bytes,
                maintype="text",
                subtype="csv",
                filename=f"fmeda_{name}.csv",
            )
        for name in getattr(review, 'hazop_names', []):
            doc = next((d for d in self.hazop_docs if d.name == name), None)
            if not doc:
                continue
            out = StringIO()
            writer = csv.writer(out)
            columns = [
                "Function",
                "Malfunction",
                "Type",
                "Scenario",
                "Conditions",
                "Hazard",
                "Safety",
                "Rationale",
                "Covered",
                "Covered By",
            ]
            writer.writerow(columns)
            for e in doc.entries:
                writer.writerow([
                    self.get_entry_field(e, "function"),
                    self.get_entry_field(e, "malfunction"),
                    self.get_entry_field(e, "mtype"),
                    self.get_entry_field(e, "scenario"),
                    self.get_entry_field(e, "conditions"),
                    self.get_entry_field(e, "hazard"),
                    "Yes" if self.get_entry_field(e, "safety", False) else "No",
                    self.get_entry_field(e, "rationale"),
                    "Yes" if self.get_entry_field(e, "covered", False) else "No",
                    self.get_entry_field(e, "covered_by"),
                ])
            csv_bytes = out.getvalue().encode("utf-8")
            out.close()
            msg.add_attachment(
                csv_bytes,
                maintype="text",
                subtype="csv",
                filename=f"hazop_{name}.csv",
            )
        for name in getattr(review, 'hara_names', []):
            doc = next((d for d in self.hara_docs if d.name == name), None)
            if not doc:
                continue
            out = StringIO()
            writer = csv.writer(out)
            columns = [
                "Malfunction",
                "Severity",
                "Severity Rationale",
                "Controllability",
                "Cont. Rationale",
                "Exposure",
                "Exp. Rationale",
                "ASIL",
                "Safety Goal",
            ]
            writer.writerow(columns)
            for e in doc.entries:
                writer.writerow([
                    self.get_entry_field(e, "malfunction"),
                    self.get_entry_field(e, "severity"),
                    self.get_entry_field(e, "sev_rationale"),
                    self.get_entry_field(e, "controllability"),
                    self.get_entry_field(e, "cont_rationale"),
                    self.get_entry_field(e, "exposure"),
                    self.get_entry_field(e, "exp_rationale"),
                    self.get_entry_field(e, "asil"),
                    self.get_entry_field(e, "safety_goal"),
                ])
            csv_bytes = out.getvalue().encode("utf-8")
            out.close()
            msg.add_attachment(
                csv_bytes,
                maintype="text",
                subtype="csv",
                filename=f"hara_{name}.csv",
            )
            port = cfg.get('port', 465)
            if port == 465:
                with smtplib.SMTP_SSL(cfg['server'], port) as server:
                    server.login(cfg['email'], cfg['password'])
                    server.send_message(msg)
            else:
                with smtplib.SMTP(cfg['server'], port) as server:
                    server.starttls()
                    server.login(cfg['email'], cfg['password'])
                    server.send_message(msg)
        except smtplib.SMTPAuthenticationError:
            messagebox.showerror(
                "Email",
                "Login failed. If your account uses two-factor authentication, "
                "create an app password and use that instead of your normal password."
            )
            self.email_config = None
        except (socket.gaierror, ConnectionRefusedError, smtplib.SMTPConnectError) as e:
            messagebox.showerror(
                "Email",
                "Failed to connect to the SMTP server. Check the address, port and internet connection."
            )
            self.email_config = None
        except Exception as e:
            messagebox.showerror("Email", f"Failed to send review email: {e}")
    def review_is_closed(self):
        if not self.review_data:
            return False
        if getattr(self.review_data, "closed", False):
            return True
        if self.review_data.due_date:
            try:
                due = datetime.datetime.strptime(self.review_data.due_date, "%Y-%m-%d").date()
                if datetime.date.today() > due:
                    return True
            except ValueError:
                pass
        return False
    def review_is_closed_for(self, review):
        if not review:
            return False
        if getattr(review, "closed", False):
            return True
        if review.due_date:
            try:
                due = datetime.datetime.strptime(review.due_date, "%Y-%m-%d").date()
                if datetime.date.today() > due:
                    return True
            except ValueError:
                pass
        return False
    def get_requirements_for_review(self, review):
        """Return a set of requirement IDs included in the given review."""
        req_ids = set()
        for tid in getattr(review, "fta_ids", []):
            node = self.find_node_by_id_all(tid)
            if not node:
                continue
            for n in self.get_all_nodes(node):
                for r in getattr(n, "safety_requirements", []):
                    req_ids.add(r.get("id"))
        for name in getattr(review, "fmea_names", []):
            fmea = next((f for f in self.fmeas if f["name"] == name), None)
            if not fmea:
                continue
            for e in fmea.get("entries", []):
                for r in e.get("safety_requirements", []):
                    req_ids.add(r.get("id"))
        return req_ids
    def update_requirement_statuses(self):
        status_order = {
            "draft": 0,
            "in review": 1,
            "peer reviewed": 2,
            "pending approval": 3,
            "approved": 4,
        for req in global_requirements.values():
            req.setdefault("status", "draft")
        for review in self.reviews:
            ids = self.get_requirements_for_review(review)
            closed = self.review_is_closed_for(review)
            for rid in ids:
                req = global_requirements.get(rid)
                if not req:
                    continue
                if review.mode == "joint":
                    if review.approved:
                        status = "approved"
                    elif closed:
                        status = "pending approval"
                    else:
                        status = "in review"
                else:  # peer review
                    if getattr(review, "reviewed", False) or closed:
                        status = "peer reviewed"
                    else:
                        status = "in review"
                if status_order[status] > status_order.get(req.get("status", "draft"), 0):
                    req["status"] = status
    def compute_requirement_asil(self, req_id):
        """Return highest ASIL across all safety goals linked to the requirement."""
        goals = self.get_requirement_goal_names(req_id)
        asil = "QM"
        for g in goals:
            a = self.get_safety_goal_asil(g)
            if ASIL_ORDER.get(a, 0) > ASIL_ORDER.get(asil, 0):
                asil = a
        return asil
    def find_safety_goal_node(self, name):
        for te in self.top_events:
            if name in (te.safety_goal_description, te.user_name):
                return te
        return None
    def compute_validation_criteria(self, req_id):
        goals = self.get_requirement_goal_names(req_id)
        vals = []
        for g in goals:
            sg = self.find_safety_goal_node(g)
            if not sg:
                continue
            try:
                acc = float(getattr(sg, "validation_target", 1.0))
            except (TypeError, ValueError):
                acc = 1.0
            try:
                sev = float(getattr(sg, "severity", 3)) / 3.0
            except (TypeError, ValueError):
                sev = 1.0
            try:
                cont = float(getattr(sg, "controllability", 3)) / 3.0
            except (TypeError, ValueError):
                cont = 1.0
            vals.append(acc * sev * cont)
        return sum(vals) / len(vals) if vals else 0.0
    def update_validation_criteria(self, req_id):
        req = global_requirements.get(req_id)
        if not req:
            return
        req["validation_criteria"] = self.compute_validation_criteria(req_id)
    def update_requirement_asil(self, req_id):
        req = global_requirements.get(req_id)
        if not req:
            return
        req["asil"] = self.compute_requirement_asil(req_id)
    def update_all_validation_criteria(self):
        for rid in global_requirements:
            self.update_validation_criteria(rid)
    def update_all_requirement_asil(self):
        for rid, req in global_requirements.items():
            if req.get("parent_id"):
                continue  # keep decomposition ASIL
            self.update_requirement_asil(rid)
    def update_base_event_requirement_asil(self):
        """Update ASIL for requirements allocated to base events."""
        for node in self.get_all_nodes(self.root_node):
            if getattr(node, "node_type", "").upper() != "BASIC EVENT":
                continue
            for req in getattr(node, "safety_requirements", []):
                rid = req.get("id")
                if not rid:
                    continue
                asil = self.compute_requirement_asil(rid)
                req["asil"] = asil
                if rid in global_requirements:
                    global_requirements[rid]["asil"] = asil
    def ensure_asil_consistency(self):
        """Sync safety goal ASILs from risk assessments and update requirement ASILs."""
        self.update_fta_statuses()
        self.sync_hara_to_safety_goals()
        self.update_hazard_list()
        self.update_all_requirement_asil()
        self.update_all_validation_criteria()
    def invalidate_reviews_for_hara(self, name):
        """Reopen reviews associated with the given risk assessment."""
        for r in self.reviews:
            if name in getattr(r, "hara_names", []):
                r.closed = False
                r.approved = False
                r.reviewed = False
                for p in r.participants:
                    p.done = False
                    p.approved = False
        self.update_hara_statuses()
        self.update_fta_statuses()
    def invalidate_reviews_for_requirement(self, req_id):
        """Reopen reviews that include the given requirement."""
        for r in self.reviews:
            if req_id in self.get_requirements_for_review(r):
                r.closed = False
                r.approved = False
                r.reviewed = False
                for p in r.participants:
                    p.done = False
                    p.approved = False
        self.update_requirement_statuses()
    def add_version(self):
        version_num = len(self.versions) + 1
        name = f"v{version_num}"
        baseline = simpledialog.askstring(
            "Baseline Name", "Enter baseline name (optional):"
        )
        if baseline:
            name += f" - {baseline}"
        # Exclude the versions list when capturing a snapshot to avoid
        # recursively embedding previous versions within each saved state.
        data = self.export_model_data(include_versions=False)
        self.versions.append({"name": name, "data": data})
    def compare_versions(self):
        if not self.versions:
            messagebox.showinfo("Versions", "No previous versions")
            return
        if hasattr(self, "_compare_tab") and self._compare_tab.winfo_exists():
            self.doc_nb.select(self._compare_tab)
            return
        self._compare_tab = self._new_tab("Compare")
        dlg = VersionCompareDialog(self._compare_tab, self)
        dlg.pack(fill=tk.BOTH, expand=True)
    def merge_review_comments(self):
        path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        with open(path, "r") as f:
            data = json.load(f)
        for rd in data.get("reviews", []):
            participants = [ReviewParticipant(**p) for p in rd.get("participants", [])]
            comments = [ReviewComment(**c) for c in rd.get("comments", [])]
            moderators = [ReviewParticipant(**m) for m in rd.get("moderators", [])]
            if not moderators and rd.get("moderator"):
                moderators = [ReviewParticipant(rd.get("moderator"), "", "moderator")]
            review = next((r for r in self.reviews if r.name == rd.get("name", "")), None)
            if review is None:
                review = ReviewData(
                    name=rd.get("name", ""),
                    description=rd.get("description", ""),
                    mode=rd.get("mode", "peer"),
                    moderators=moderators,
                    participants=participants,
                    comments=comments,
                    approved=rd.get("approved", False),
                    fta_ids=rd.get("fta_ids", []),
                    fmea_names=rd.get("fmea_names", []),
                    fmeda_names=rd.get("fmeda_names", []),
                    hazop_names=rd.get("hazop_names", []),
                    hara_names=rd.get("hara_names", []),
                    stpa_names=rd.get("stpa_names", []),
                    fi2tc_names=rd.get("fi2tc_names", []),
                    tc2fi_names=rd.get("tc2fi_names", []),
                    due_date=rd.get("due_date", ""),
                    closed=rd.get("closed", False),
                )
                self.reviews.append(review)
                continue
            for p in participants:
                if all(p.name != ep.name for ep in review.participants):
                    review.participants.append(p)
            for m in moderators:
                if all(m.name != em.name for em in review.moderators):
                    review.moderators.append(m)
            review.due_date = rd.get("due_date", review.due_date)
            review.closed = rd.get("closed", review.closed)
            next_id = len(review.comments) + 1
            for c in comments:
                review.comments.append(ReviewComment(next_id, c.node_id, c.text, c.reviewer,
                                                     target_type=c.target_type, req_id=c.req_id,
                                                     field=c.field, resolved=c.resolved,
                                                     resolution=c.resolution))
                next_id += 1
        messagebox.showinfo("Merge", "Comments merged")
    def calculate_diff_nodes(self, old_data):
        old_map = self.node_map_from_data(old_data["top_events"])
        new_map = self.node_map_from_data([e.to_dict() for e in self.top_events])
        changed = []
        for nid, nd in new_map.items():
            if nid not in old_map:
                changed.append(nid)
            elif json.dumps(old_map[nid], sort_keys=True) != json.dumps(nd, sort_keys=True):
                changed.append(nid)
        return changed
    def calculate_diff_between(self, data1, data2):
        map1 = self.node_map_from_data(data1["top_events"])
        map2 = self.node_map_from_data(data2["top_events"])
        changed = []
        for nid, nd in map2.items():
            if nid not in map1 or json.dumps(map1.get(nid, {}), sort_keys=True) != json.dumps(nd, sort_keys=True):
                changed.append(nid)
        return changed
    def node_map_from_data(self, top_events):
        result = {}
        def visit(d):
            result[d["unique_id"]] = d
            for ch in d.get("children", []):
                visit(ch)
        for t in top_events:
            visit(t)
        return result
    def set_current_user(self):
        if not self.review_data:
            messagebox.showwarning("User", "Start a review first")
        parts = self.review_data.participants + self.review_data.moderators
        dlg = ReviewUserSelectDialog(self.root, parts, initial_name=self.current_user)
        if not dlg.result:
        name, _ = dlg.result
        allowed = [p.name for p in parts]
        if name not in allowed:
            messagebox.showerror("User", "Name not found in participants")
            return
        self.current_user = name
    def get_current_user_role(self):
        if not self.review_data:
            return None
        if self.current_user in [m.name for m in self.review_data.moderators]:
            return "moderator"
        for p in self.review_data.participants:
            if p.name == self.current_user:
                return p.role
        return None
    def focus_on_node(self, node):
        self.selected_node = node
        try:
            if hasattr(self, "canvas") and self.canvas is not None and self.canvas.winfo_exists():
                self.redraw_canvas()
                bbox = self.canvas.bbox("all")
                if bbox:
                    self.canvas.xview_moveto(max(0, (node.x * self.zoom - self.canvas.winfo_width()/2) / bbox[2]))
                    self.canvas.yview_moveto(max(0, (node.y * self.zoom - self.canvas.winfo_height()/2) / bbox[3]))
        except tk.TclError:
            pass
    def get_review_targets(self):
        targets = []
        target_map = {}
        # Determine which FTAs and FMEAs are part of the current review.
        if self.review_data:
            allowed_ftas = set(self.review_data.fta_ids)
            allowed_fmeas = set(self.review_data.fmea_names)
            allowed_fmedas = set(getattr(self.review_data, 'fmeda_names', []))
            allowed_ftas = set()
            allowed_fmeas = set()
            allowed_fmedas = set()
        # Collect nodes from the selected FTAs (or all if none selected).
        nodes = []
        if allowed_ftas:
            for te in self.top_events:
                if te.unique_id in allowed_ftas:
                    nodes.extend(self.get_all_nodes(te))
        else:
            nodes = self.get_all_nodes_in_model()
        # Determine which nodes have FMEA entries in the selected FMEAs.
        fmea_node_ids = set()
        if allowed_fmeas or allowed_fmedas:
            for fmea in self.fmeas:
                if fmea["name"] in allowed_fmeas:
                    fmea_node_ids.update(be.unique_id for be in fmea["entries"])
            for d in self.fmedas:
                if d["name"] in allowed_fmedas:
                    fmea_node_ids.update(be.unique_id for be in d["entries"])
        else:
            # When no FMEA was selected, do not offer FMEA-related targets
            fmea_node_ids = set()
        for node in nodes:
            label = node.user_name or node.description or f"Node {node.unique_id}"
            targets.append(label)
            target_map[label] = ("node", node.unique_id)
            if hasattr(node, "safety_requirements"):
                for req in node.safety_requirements:
                    rlabel = f"{label} [Req {req.get('id')}]"
                    targets.append(rlabel)
                    target_map[rlabel] = ("requirement", node.unique_id, req.get("id"))
            if node.node_type.upper() == "BASIC EVENT" and node.unique_id in fmea_node_ids:
                flabel = f"{label} [FMEA]"
                targets.append(flabel)
                target_map[flabel] = ("fmea", node.unique_id)
                for field in ["Failure Mode", "Effect", "Cause", "Severity", "Occurrence", "Detection", "RPN"]:
                    slabel = f"{label} [FMEA {field}]"
                    key = field.lower().replace(' ', '_')
                    target_map[slabel] = ("fmea_field", node.unique_id, key)
                    targets.append(slabel)
        return targets, target_map
