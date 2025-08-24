"""Review and version management extracted from AutoML."""
import datetime
import html
import csv
import json
from email.message import EmailMessage
from email.utils import make_msgid
import smtplib
import socket
from io import BytesIO, StringIO
import tkinter as tk
from tkinter import simpledialog, filedialog
from gui import messagebox
from gui.review_toolbox import (
    ReviewToolbox,
    ReviewData,
    ReviewParticipant,
    ReviewComment,
    ParticipantDialog,
    EmailConfigDialog,
    ReviewScopeDialog,
    ReviewDocumentDialog,
    VersionCompareDialog,
)
from gui.dialog_utils import askstring_fixed


class ReviewManager:
    """Handle peer and joint reviews and version comparison."""

    def __init__(self, app):
        self.app = app
    def start_peer_review(self):
        dialog = ParticipantDialog(self.app.root, joint=False)

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
            if any(r.name == name for r in self.app.reviews):
                messagebox.showerror("Review", "Name already exists")
                return
            scope = ReviewScopeDialog(self.app.root, self.app)
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
            self.app.reviews.append(review)
            self.app.review_data = review
            self.app.current_user = moderators[0].name if moderators else parts[0].name
            self.open_review_document(review)
            self.send_review_email(review)
            self.open_review_toolbox()
    def start_joint_review(self):
        dialog = ParticipantDialog(self.app.root, joint=True)
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
            if any(r.name == name for r in self.app.reviews):
                messagebox.showerror("Review", "Name already exists")
                return
            scope = ReviewScopeDialog(self.app.root, self.app)
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

            def peer_completed(pred):
                return any(
                    r.mode == 'peer'
                    and getattr(r, 'reviewed', False)
                    and pred(r)
                    for r in self.app.reviews
                )

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
            self.app.reviews.append(review)
            self.app.review_data = review
            self.app.current_user = moderators[0].name if moderators else participants[0].name
            self.open_review_document(review)
            self.send_review_email(review)
            self.open_review_toolbox()
    def open_review_document(self, review):
        if hasattr(self.app, "_review_doc_tab") and self.app._review_doc_tab.winfo_exists():
            self.app.doc_nb.select(self.app._review_doc_tab)
        else:
            title = f"Review {review.name}"
            self.app._review_doc_tab = self.app._new_tab(title)
            self.app._review_doc_window = ReviewDocumentDialog(self.app._review_doc_tab, self.app, review)
            self.app._review_doc_window.pack(fill=tk.BOTH, expand=True)
        self.app.refresh_all()

    def open_review_toolbox(self):
        if not self.app.reviews:
            messagebox.showwarning("Review", "No reviews defined")
            return
        if not self.app.review_data and self.app.reviews:
            self.app.review_data = self.app.reviews[0]
        self.app.update_hara_statuses()
        self.app.update_fta_statuses()
        self.app.update_requirement_statuses()
        if hasattr(self.app, "_review_tab") and self.app._review_tab.winfo_exists():
            self.app.doc_nb.select(self.app._review_tab)
        else:
            self.app._review_tab = self.app._new_tab("Review")
            self.app.review_window = ReviewToolbox(self.app._review_tab, self.app)
            self.app.review_window.pack(fill=tk.BOTH, expand=True)
        self.app.refresh_all()
        self.app.user_manager.set_current_user()
    def send_review_email(self, review):
        """Send the review summary to all reviewers via configured SMTP."""
        recipients = [p.email for p in review.participants if p.role == 'reviewer' and p.email]
        if not recipients:
            return
        current_email = next((p.email for p in review.participants if p.name == self.app.current_user), "")
        if not getattr(self.app, "email_config", None):
            cfg = EmailConfigDialog(self.app.root, default_email=current_email).result
            self.app.email_config = cfg
        cfg = getattr(self.app, "email_config", None)
        if not cfg:
            return
        subject = f"Review: {review.name}"
        lines = [f"Review Name: {review.name}", f"Description: {review.description}", ""]
        if review.fta_ids:
            lines.append("FTAs:")
            for tid in review.fta_ids:
                te = next((t for t in self.app.top_events if t.unique_id == tid), None)
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
            node = self.app.find_node_by_id_all(tid)
            if not node:
                continue
            img = self.app.capture_diff_diagram(node)
            if img is None:
                continue
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            cid = make_msgid()
            label = node.user_name or node.name or f"id{tid}"
            html_lines.append(
                f"<p><b>FTA: {html.escape(label)}</b><br>"
                f"<img src=\"cid:{cid[1:-1]}\" alt=\"{html.escape(label)}\"></p>"
            )
            image_cids.append(cid)
            images.append(buf.getvalue())
        diff_html = self.app.build_requirement_diff_html(review)
        if diff_html:
            html_lines.append("<b>Requirements:</b><br>" + diff_html)
        html_lines.append("</body></html>")
        html_body = "\n".join(html_lines)
        msg.add_alternative(html_body, subtype="html")
        html_part = msg.get_payload()[1]
        for cid, data in zip(image_cids, images):
            html_part.add_related(data, "image", "png", cid=cid)
        for name in review.fmea_names:
            fmea = next((f for f in self.app.fmeas if f["name"] == name), None)
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
                src = self.app.get_failure_mode_node(be)
                comp = self.app.get_component_name_for_node(src) or "N/A"
                parent = src.parents[0] if src.parents else None
                parent_name = parent.user_name if parent and getattr(parent, "node_type", "").upper() not in GATE_NODE_TYPES else ""
                req_ids = "; ".join([f"{req['req_type']}:{req['text']}" for req in getattr(be, 'safety_requirements', [])])
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
            msg.add_attachment(csv_bytes, maintype="text", subtype="csv", filename=f"fmea_{name}.csv")
        for name in getattr(review, 'fmeda_names', []):
            fmeda = next((f for f in self.app.fmedas if f["name"] == name), None)
            if not fmeda:
                continue
            out = StringIO()
            writer = csv.writer(out)
            columns = [
                "Component","Parent","Failure Mode","Malfunction","Safety Goal","FaultType","Fraction","FIT","DiagCov","Mechanism",
            ]
            writer.writerow(columns)
            for be in fmeda["entries"]:
                src = self.app.get_failure_mode_node(be)
                comp = self.app.get_component_name_for_node(src) or "N/A"
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
            msg.add_attachment(csv_bytes, maintype="text", subtype="csv", filename=f"fmeda_{name}.csv")
        for name in getattr(review, 'hazop_names', []):
            doc = next((d for d in self.app.hazop_docs if d.name == name), None)
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
                    self.app.get_entry_field(e, "function"),
                    self.app.get_entry_field(e, "malfunction"),
                    self.app.get_entry_field(e, "mtype"),
                    self.app.get_entry_field(e, "scenario"),
                    self.app.get_entry_field(e, "conditions"),
                    self.app.get_entry_field(e, "hazard"),
                    "Yes" if self.app.get_entry_field(e, "safety", False) else "No",
                    self.app.get_entry_field(e, "rationale"),
                    "Yes" if self.app.get_entry_field(e, "covered", False) else "No",
                    self.app.get_entry_field(e, "covered_by"),
                ])
            csv_bytes = out.getvalue().encode("utf-8")
            out.close()
            msg.add_attachment(csv_bytes, maintype="text", subtype="csv", filename=f"hazop_{name}.csv")
        for name in getattr(review, 'hara_names', []):
            doc = next((d for d in self.app.hara_docs if d.name == name), None)
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
                    self.app.get_entry_field(e, "malfunction"),
                    self.app.get_entry_field(e, "severity"),
                    self.app.get_entry_field(e, "sev_rationale"),
                    self.app.get_entry_field(e, "controllability"),
                    self.app.get_entry_field(e, "cont_rationale"),
                    self.app.get_entry_field(e, "exposure"),
                    self.app.get_entry_field(e, "exp_rationale"),
                    self.app.get_entry_field(e, "asil"),
                    self.app.get_entry_field(e, "safety_goal"),
                ])
            csv_bytes = out.getvalue().encode("utf-8")
            out.close()
            msg.add_attachment(csv_bytes, maintype="text", subtype="csv", filename=f"hara_{name}.csv")
        try:
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
            self.app.email_config = None
        except (socket.gaierror, ConnectionRefusedError, smtplib.SMTPConnectError):
            messagebox.showerror(
                "Email",
                "Failed to connect to the SMTP server. Check the address, port and internet connection."
            )
            self.app.email_config = None
        except Exception as e:
            messagebox.showerror("Email", f"Failed to send review email: {e}")
    def review_is_closed(self):
        if not self.app.review_data:
            return False
        if getattr(self.app.review_data, "closed", False):
            return True
        if self.app.review_data.due_date:
            try:
                due = datetime.datetime.strptime(self.app.review_data.due_date, "%Y-%m-%d").date()
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
            node = self.app.find_node_by_id_all(tid)
            if not node:
                continue
            for n in self.app.get_all_nodes(node):
                for r in getattr(n, "safety_requirements", []):
                    req_ids.add(r.get("id"))
        for name in getattr(review, "fmea_names", []):
            fmea = next((f for f in self.app.fmeas if f["name"] == name), None)
            if not fmea:
                continue
            for e in fmea.get("entries", []):
                for r in e.get("safety_requirements", []):
                    req_ids.add(r.get("id"))
        return req_ids
    def invalidate_reviews_for_hara(self, name):
        """Reopen reviews associated with the given risk assessment."""
        for r in self.app.reviews:
            if name in getattr(r, "hara_names", []):
                r.closed = False
                r.approved = False
                r.reviewed = False
                for p in r.participants:
                    p.done = False
                    p.approved = False
        self.app.update_hara_statuses()
        self.app.update_fta_statuses()

    def invalidate_reviews_for_requirement(self, req_id):
        """Reopen reviews that include the given requirement."""
        for r in self.app.reviews:
            if req_id in self.get_requirements_for_review(r):
                r.closed = False
                r.approved = False
                r.reviewed = False
                for p in r.participants:
                    p.done = False
                    p.approved = False
        self.app.update_requirement_statuses()
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
            review = next((r for r in self.app.reviews if r.name == rd.get("name", "")), None)
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
                self.app.reviews.append(review)
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
                review.comments.append(
                    ReviewComment(
                        next_id,
                        c.node_id,
                        c.text,
                        c.reviewer,
                        target_type=c.target_type,
                        req_id=c.req_id,
                        field=c.field,
                        resolved=c.resolved,
                        resolution=c.resolution,
                    )
                )
                next_id += 1
        messagebox.showinfo("Merge", "Comments merged")
    def add_version(self):
        version_num = len(self.app.versions) + 1
        name = f"v{version_num}"
        baseline = simpledialog.askstring(
            "Baseline Name", "Enter baseline name (optional):"
        )
        if baseline:
            name += f" - {baseline}"
        data = self.app.export_model_data(include_versions=False)
        self.app.versions.append({"name": name, "data": data})

    def compare_versions(self):
        if not self.app.versions:
            messagebox.showinfo("Versions", "No previous versions")
            return
        if hasattr(self.app, "_compare_tab") and self.app._compare_tab.winfo_exists():
            self.app.doc_nb.select(self.app._compare_tab)
            return
        self.app._compare_tab = self.app._new_tab("Compare")
        dlg = VersionCompareDialog(self.app._compare_tab, self.app)
        dlg.pack(fill=tk.BOTH, expand=True)
    def get_review_targets(self):
        targets = []
        target_map = {}
        if self.app.review_data:
            allowed_ftas = set(self.app.review_data.fta_ids)
            allowed_fmeas = set(self.app.review_data.fmea_names)
            allowed_fmedas = set(getattr(self.app.review_data, 'fmeda_names', []))
        else:
            allowed_ftas = set()
            allowed_fmeas = set()
            allowed_fmedas = set()
        nodes = []
        if allowed_ftas:
            for te in self.app.top_events:
                if te.unique_id in allowed_ftas:
                    nodes.extend(self.app.get_all_nodes(te))
        else:
            nodes = self.app.get_all_nodes_in_model()
        fmea_node_ids = set()
        if allowed_fmeas or allowed_fmedas:
            for fmea in self.app.fmeas:
                if fmea["name"] in allowed_fmeas:
                    fmea_node_ids.update(be.unique_id for be in fmea["entries"])
            for d in self.app.fmedas:
                if d["name"] in allowed_fmedas:
                    fmea_node_ids.update(be.unique_id for be in d["entries"])
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

    def calculate_diff_nodes(self, old_data):
        old_map = self.node_map_from_data(old_data["top_events"])
        new_map = self.node_map_from_data([e.to_dict() for e in self.app.top_events])
        changed = []
        for nid, nd in new_map.items():
            if nid not in old_map or json.dumps(old_map.get(nid, {}), sort_keys=True) != json.dumps(nd, sort_keys=True):
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
