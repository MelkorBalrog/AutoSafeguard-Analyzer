        "HAZOP": "Risk Assessment",
        "Risk Assessment": None,
        "STPA": "Risk Assessment",
        "FI2TC": "Risk Assessment",
        "TC2FI": "Risk Assessment",
        "FTA": "Quantitative Analysis",
        # --- Risk Assessment Menu ---
        risk_menu = tk.Menu(menubar, tearoff=0)
        risk_menu.add_command(
            (risk_menu, risk_menu.index("end"))
        risk_menu.add_command(
            (risk_menu, risk_menu.index("end"))
        risk_menu.add_command(
            (risk_menu, risk_menu.index("end"))
        risk_menu.add_command(
            label="Hazard Explorer", command=self.show_hazard_explorer
        risk_menu.add_command(
            label="Hazards Editor", command=self.show_hazard_editor
        risk_menu.add_command(
            label="Malfunctions Editor", command=self.show_malfunction_editor
        )
        risk_menu.add_command(label="Faults Editor", command=self.show_fault_editor)
        risk_menu.add_command(label="Failures Editor", command=self.show_failure_editor)
        risk_menu.add_separator()
        risk_menu.add_command(
            label="Triggering Conditions", command=self.show_triggering_condition_list
        )
        risk_menu.add_command(
            label="Functional Insufficiencies",
            command=self.show_functional_insufficiency_list,
        )
        risk_menu.add_command(
            label="Malfunctions Editor", command=self.show_malfunctions_editor
        )
        risk_menu.add_separator()
        risk_menu.add_command(
            (risk_menu, risk_menu.index("end"))
        risk_menu.add_command(
            (risk_menu, risk_menu.index("end"))
        )

        # --- Qualitative Analysis Menu ---
        self.qualitative_menu = tk.Menu(menubar, tearoff=0)
        qualitative_menu = self.qualitative_menu
        qualitative_menu.add_command(
            label="Threat Analysis",
            command=self.open_threat_window,
            state=tk.DISABLED,
        )
        self.work_product_menus.setdefault("Threat Analysis", []).append(
        quantitative_menu.add_cascade(label="FTA", menu=fta_menu, state=tk.DISABLED)
        self.work_product_menus.setdefault("FTA", []).append(
            (quantitative_menu, quantitative_menu.index("end"))
        )

        menubar.add_cascade(label="Risk Assessment", menu=risk_menu)
        idx = menubar.index("end")
        self.work_product_menus.setdefault("Risk Assessment", []).append((menubar, idx))
        menubar.entryconfig(idx, state=tk.DISABLED)
