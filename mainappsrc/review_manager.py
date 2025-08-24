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
from gui.style_manager import StyleManager
from analysis.fmeda_utils import GATE_NODE_TYPES


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
            img = self.capture_diff_diagram(node)
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
    def capture_diff_diagram(self, top_event):
        """Return an image of the FTA with diff colouring versus last version."""
        if not self.app.versions:
            return self.app.diagram_renderer.capture_page_diagram(top_event)
        from io import BytesIO
        from PIL import Image
        import difflib
        import sys
        current = self.app.export_model_data(include_versions=False)
        base_data = self.app.versions[-1]["data"]

        def filter_events(data):
            return [t for t in data.get("top_events", []) if t["unique_id"] == top_event.unique_id]

        data1 = {"top_events": filter_events(base_data)}
        data2 = {"top_events": filter_events(current)}

        map1 = self.app.node_map_from_data(data1["top_events"])
        map2 = self.app.node_map_from_data(data2["top_events"])

        def build_conn_set(events):
            conns = set()

            def visit(d):
                for ch in d.get("children", []):
                    conns.add((d["unique_id"], ch["unique_id"]))
                    visit(ch)

            for t in events:
                visit(t)
            return conns

        conns1 = build_conn_set(data1["top_events"])
        conns2 = build_conn_set(data2["top_events"])

        conn_status = {}
        for c in conns1 | conns2:
            if c in conns1 and c not in conns2:
                conn_status[c] = "removed"
            elif c in conns2 and c not in conns1:
                conn_status[c] = "added"
            else:
                conn_status[c] = "existing"

        status = {}
        for nid in set(map1) | set(map2):
            if nid in map1 and nid not in map2:
                status[nid] = "removed"
            elif nid in map2 and nid not in map1:
                status[nid] = "added"
            else:
                if json.dumps(map1[nid], sort_keys=True) != json.dumps(map2[nid], sort_keys=True):
                    status[nid] = "added"
                else:
                    status[nid] = "existing"

        module = sys.modules.get(self.app.__class__.__module__)
        FaultTreeNodeCls = getattr(module, "FaultTreeNode", None)
        if not FaultTreeNodeCls and self.app.top_events:
            FaultTreeNodeCls = type(self.app.top_events[0])
        new_roots = [FaultTreeNodeCls.from_dict(t) for t in data2["top_events"]]
        removed_ids = [nid for nid, st in status.items() if st == "removed"]
        for rid in removed_ids:
            if rid in map1:
                nd = map1[rid]
                new_roots.append(FaultTreeNodeCls.from_dict(nd))

        allow_ids = set()

        def collect_ids(d):
            allow_ids.add(d["unique_id"])
            for ch in d.get("children", []):
                collect_ids(ch)

        if top_event.unique_id in map1:
            collect_ids(map1[top_event.unique_id])
        if top_event.unique_id in map2:
            collect_ids(map2[top_event.unique_id])

        node_objs = {}

        def collect_nodes(n):
            if n.unique_id not in node_objs:
                node_objs[n.unique_id] = n
            for ch in n.children:
                collect_nodes(ch)

        for r in new_roots:
            collect_nodes(r)

        def diff_segments(old, new):
            matcher = difflib.SequenceMatcher(None, old, new)
            segments = []
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == "equal":
                    segments.append((old[i1:i2], "black"))
                elif tag == "delete":
                    segments.append((old[i1:i2], "red"))
                elif tag == "insert":
                    segments.append((new[j1:j2], "blue"))
                elif tag == "replace":
                    segments.append((old[i1:i2], "red"))
                    segments.append((new[j1:j2], "blue"))
            return segments

        def draw_segment_text(canvas, cx, cy, segments, font_obj):
            lines = [[]]
            for text, color in segments:
                parts = text.split("\n")
                for idx, part in enumerate(parts):
                    if idx > 0:
                        lines.append([])
                    lines[-1].append((part, color))
            line_height = font_obj.metrics("linespace")
            total_height = line_height * len(lines)
            start_y = cy - total_height / 2
            for line in lines:
                line_width = sum(font_obj.measure(part) for part, _ in line)
                start_x = cx - line_width / 2
                x = start_x
                for part, color in line:
                    if part:
                        canvas.create_text(x, start_y, text=part, anchor="nw", fill=color, font=font_obj)
                        x += font_obj.measure(part)
                start_y += line_height

        temp = tk.Toplevel(self.app.root)
        temp.withdraw()
        canvas = tk.Canvas(temp, bg=StyleManager.get_instance().canvas_bg, width=2000, height=2000)
        canvas.pack()

        def draw_connections(n):
            if n.unique_id not in allow_ids:
                for ch in n.children:
                    draw_connections(ch)
                return
            region_width = 60
            parent_bottom = (n.x, n.y + 20)
            for i, ch in enumerate(n.children):
                if ch.unique_id not in allow_ids:
                    continue
                parent_conn = (
                    n.x - region_width / 2 + (i + 0.5) * (region_width / len(n.children)),
                    parent_bottom[1],
                )
                child_top = (ch.x, ch.y - 25)
                edge_st = conn_status.get((n.unique_id, ch.unique_id), "existing")
                if status.get(n.unique_id) == "removed" or status.get(ch.unique_id) == "removed":
                    edge_st = "removed"
                color = "gray"
                if edge_st == "added":
                    color = "blue"
                elif edge_st == "removed":
                    color = "red"
                if self.app.fta_drawing_helper:
                    self.app.fta_drawing_helper.draw_90_connection(canvas, parent_conn, child_top, outline_color=color, line_width=1)
                draw_connections(ch)

        def draw_node(n):
            if n.unique_id not in allow_ids:
                for ch in n.children:
                    draw_node(ch)
                return
            st = status.get(n.unique_id, "existing")
            color = "dimgray"
            if st == "added":
                color = "blue"
            elif st == "removed":
                color = "red"

            source = n if getattr(n, "is_primary_instance", True) else getattr(n, "original", n)
            subtype_text = source.input_subtype if source.input_subtype else "N/A"
            display_label = source.display_label
            old_data = map1.get(n.unique_id)
            new_data = map2.get(n.unique_id)

            if old_data and new_data:
                desc_segments = [("Desc: ", "black")] + diff_segments(
                    old_data.get("description", ""), new_data.get("description", "")
                )
                rat_segments = [("Rationale: ", "black")] + diff_segments(
                    old_data.get("rationale", ""), new_data.get("rationale", "")
                )
            else:
                desc_segments = [("Desc: " + source.description, "black")]
                rat_segments = [("Rationale: " + source.rationale, "black")]
            segments = [
                (f"Type: {source.node_type}\n", "black"),
                (f"Subtype: {subtype_text}\n", "black"),
                (f"{display_label}\n", "black"),
            ] + desc_segments + [("\n\n", "black")] + rat_segments

            top_text = "".join(seg[0] for seg in segments)
            bottom_text = n.name
            fill = self.app.get_node_fill_color(n, getattr(canvas, "diagram_mode", None))
            eff_x, eff_y = n.x, n.y
            typ = n.node_type.upper()
            items_before = canvas.find_all()
            if typ in GATE_NODE_TYPES:
                if n.gate_type and n.gate_type.upper() == "OR":
                    if self.app.fta_drawing_helper:
                        self.app.fta_drawing_helper.draw_rotated_or_gate_shape(canvas, eff_x, eff_y, scale=40, top_text=top_text, bottom_text=bottom_text, fill=fill, outline_color=color, line_width=2)
                else:
                    if self.app.fta_drawing_helper:
                        self.app.fta_drawing_helper.draw_rotated_and_gate_shape(canvas, eff_x, eff_y, scale=40, top_text=top_text, bottom_text=bottom_text, fill=fill, outline_color=color, line_width=2)
            else:
                if self.app.fta_drawing_helper:
                    self.app.fta_drawing_helper.draw_circle_event_shape(canvas, eff_x, eff_y, 45, top_text=top_text, bottom_text=bottom_text, fill=fill, outline_color=color, line_width=2)

            items_after = canvas.find_all()
            text_id = None
            for item in items_after:
                if item in items_before:
                    continue
                if canvas.type(item) == "text" and canvas.itemcget(item, "text") == top_text:
                    text_id = item
                    break

            if text_id and any(c in ("red", "blue") for _, c in segments):
                bbox = canvas.bbox(text_id)
                cx = (bbox[0] + bbox[2]) / 2
                cy = (bbox[1] + bbox[3]) / 2
                canvas.itemconfigure(text_id, state="hidden")
                draw_segment_text(canvas, cx, cy, segments, self.app.diagram_font)
            for ch in n.children:
                draw_node(ch)

        for r in new_roots:
            draw_connections(r)
            draw_node(r)

        existing_pairs = set()
        for p in node_objs.values():
            for ch in p.children:
                existing_pairs.add((p.unique_id, ch.unique_id))
        for (pid, cid), st in conn_status.items():
            if st != "removed":
                continue
            if (pid, cid) in existing_pairs:
                continue
            if pid in node_objs and cid in node_objs and pid in allow_ids and cid in allow_ids:
                parent = node_objs[pid]
                child = node_objs[cid]
                parent_pt = (parent.x, parent.y + 20)
                child_pt = (child.x, child.y - 25)
                if self.app.fta_drawing_helper:
                    self.app.fta_drawing_helper.draw_90_connection(canvas, parent_pt, child_pt, outline_color="red", line_width=1)

        canvas.update()
        bbox = canvas.bbox("all")
        if not bbox:
            temp.destroy()
            return None
        x, y, x2, y2 = bbox
        ps = canvas.postscript(colormode="color", x=x, y=y, width=x2 - x, height=y2 - y)
        ps_bytes = BytesIO(ps.encode("utf-8"))
        try:
            img = Image.open(ps_bytes)
            img.load(scale=3)
        except Exception:
            img = None
        temp.destroy()
        return img.convert("RGB") if img else None
