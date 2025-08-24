        # --- Risk Assessment Menu ---
        risk_menu = tk.Menu(menubar, tearoff=0)
        risk_menu.add_command(
            (risk_menu, risk_menu.index("end"))
        risk_menu.add_command(
            (risk_menu, risk_menu.index("end"))
        risk_menu.add_command(
            (risk_menu, risk_menu.index("end"))
        risk_menu.add_command(label="Hazard Explorer", command=self.show_hazard_explorer)
        risk_menu.add_command(label="Hazards Editor", command=self.show_hazard_editor)
        risk_menu.add_command(label="Malfunctions Editor", command=self.show_malfunction_editor)
        risk_menu.add_command(label="Faults Editor", command=self.show_fault_editor)
        risk_menu.add_command(label="Failures Editor", command=self.show_failure_editor)
        risk_menu.add_separator()
        risk_menu.add_command(label="Triggering Conditions", command=self.show_triggering_condition_list)
        risk_menu.add_command(label="Functional Insufficiencies", command=self.show_functional_insufficiency_list)
        risk_menu.add_command(label="Malfunctions Editor", command=self.show_malfunctions_editor)
        risk_menu.add_separator()
        risk_menu.add_command(
            (risk_menu, risk_menu.index("end"))
        risk_menu.add_command(
            (risk_menu, risk_menu.index("end"))
        )

        # --- Qualitative Analysis Menu ---
        qualitative_menu = tk.Menu(menubar, tearoff=0)
        qualitative_menu.add_command(
            label="Threat Analysis",
            command=self.open_threat_window,
            state=tk.DISABLED,
        )
        self.work_product_menus.setdefault("Threat Analysis", []).append(

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
            state=tk.DISABLED,
        )
        fta_menu.add_command(label="Common Cause Toolbox", command=self.show_common_cause_view)
        fta_menu.add_command(label="Cause & Effect Chain", command=self.show_cause_effect_chain)
        self.fta_menu = fta_menu
        quantitative_menu.add_cascade(label="FTA", menu=fta_menu, state=tk.DISABLED)
        self.work_product_menus.setdefault("FTA", []).append(
            (quantitative_menu, quantitative_menu.index("end"))
        )
        menubar.add_cascade(label="Risk Assessment", menu=risk_menu)
        idx = menubar.index("end")
        self.work_product_menus.setdefault("Risk Assessment", []).append((menubar, idx))
        menubar.entryconfig(idx, state=tk.DISABLED)
