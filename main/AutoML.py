from gui.name_utils import unique_name_v4
from analysis.scenario_bn import build_bn_from_scenario
        def gen_bn():
            sel_lib = lib_lb.curselection()
            sel_sc = scen_tree.selection()
            if not sel_lib or not sel_sc:
                return
            lib = self.scenario_libraries[sel_lib[0]]
            idx = scen_tree.index(sel_sc[0])
            scen = lib.get("scenarios", [])[idx]
            doc = build_bn_from_scenario(scen)
            if not hasattr(self, "cbn_docs"):
                self.cbn_docs = []
            existing = [d.name for d in self.cbn_docs]
            doc.name = unique_name_v4(existing, doc.name)
            self.cbn_docs.append(doc)
            toolbox = getattr(self, "safety_mgmt_toolbox", None)
            if toolbox:
                toolbox.register_created_work_product(
                    "Causal Bayesian Network Analysis", doc.name
                )
            self.open_causal_bayesian_network_window()
            if getattr(self, "_cbn_window", None):
                self._cbn_window.refresh_docs()
                self._cbn_window.doc_var.set(doc.name)
                self._cbn_window.select_doc()

        ttk.Button(btnf, text="Gen BN", command=gen_bn).pack(side=tk.LEFT)
