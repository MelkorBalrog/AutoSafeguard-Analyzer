                # Reuse existing PAA root if it was created above
                existing = [
                    n
                    for n in tree.get_children(safety_root)
                    if tree.item(n, "text") == "PAAs"
                ]
                paa_root = existing[0] if existing else tree.insert(
                    safety_root, "end", text="PAAs", open=True
                )
                    if any(
                        tree.item(c, "text") == te.name
                        for c in tree.get_children(paa_root)
                    ):
                        continue
