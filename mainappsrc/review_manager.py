import json
import datetime
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox

from gui.review_toolbox import (
    ReviewToolbox,
    ReviewData,
    ReviewParticipant,
    ReviewComment,
    ParticipantDialog,
    ReviewScopeDialog,
    ReviewDocumentDialog,
    VersionCompareDialog,
)
from gui.dialog_utils import askstring_fixed


class ReviewManager:
    """Manage peer and joint reviews and version comparisons."""

    def __init__(self, app):
        self.app = app
        self.reviews: list[ReviewData] = []
        self.review_data: ReviewData | None = None
        self.review_window = None
        self.versions: list[dict] = []

    # ------------------------------------------------------------------
    # Review lifecycle
    # ------------------------------------------------------------------
    def start_peer_review(self):
        dialog = ParticipantDialog(self.app.root, joint=False)
        if not dialog.result:
            return
        moderators, parts = dialog.result
        name = simpledialog.askstring("Review Name", "Enter unique review name:")
        if not name:
            return
        description = askstring_fixed(
            simpledialog, "Description", "Enter a short description:",
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
            mode="peer",
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
        self.app.current_user = moderators[0].name if moderators else parts[0].name
        self.open_review_document(review)
        self.send_review_email(review)
        self.open_review_toolbox()

    def start_joint_review(self):
        dialog = ParticipantDialog(self.app.root, joint=True)
        if not dialog.result:
            return
        moderators, participants = dialog.result
        name = simpledialog.askstring("Review Name", "Enter unique review name:")
        if not name:
            return
        description = askstring_fixed(
            simpledialog, "Description", "Enter a short description:",
        )
        if description is None:
            description = ""
        if not moderators:
            messagebox.showerror("Review", "Please specify a moderator")
            return
        if not any(p.role == "reviewer" for p in participants):
            messagebox.showerror("Review", "At least one reviewer required")
            return
        if not any(p.role == "approver" for p in participants):
            messagebox.showerror("Review", "At least one approver required")
            return
        due_date = simpledialog.askstring("Due Date", "Enter due date (YYYY-MM-DD):")
        if any(r.name == name for r in self.reviews):
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
                r.mode == "peer" and getattr(r, "reviewed", False) and pred(r)
                for r in self.reviews
            )

        for tid in fta_ids:
            if not peer_completed(lambda r, tid=tid: tid in r.fta_ids):
                messagebox.showerror(
                    "Review", "Peer review must be reviewed before starting joint review",
                )
                return
        for name_fta in fmea_names:
            if not peer_completed(lambda r, n=name_fta: n in r.fmea_names):
                messagebox.showerror(
                    "Review", "Peer review must be reviewed before starting joint review",
                )
                return
        for name_fd in fmeda_names:
            if not peer_completed(lambda r, n=name_fd: n in r.fmeda_names):
                messagebox.showerror(
                    "Review", "Peer review must be reviewed before starting joint review",
                )
                return

        review = ReviewData(
            name=name,
            description=description,
            mode="joint",
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
        self.app.current_user = moderators[0].name if moderators else participants[0].name
        self.open_review_document(review)
        self.send_review_email(review)
        self.open_review_toolbox()

    def open_review_document(self, review):
        app = self.app
        if hasattr(app, "_review_doc_tab") and app._review_doc_tab.winfo_exists():
            app.doc_nb.select(app._review_doc_tab)
            return
        title = f"Review {review.name}"
        app._review_doc_tab = app._new_tab(title)
        app._review_doc_window = ReviewDocumentDialog(app._review_doc_tab, app, review)
        app._review_doc_window.pack(fill=tk.BOTH, expand=True)

    def open_review_toolbox(self):
        if not self.reviews:
            messagebox.showwarning("Review", "No reviews defined")
            return
        if not self.review_data and self.reviews:
            self.review_data = self.reviews[0]
        app = self.app
        if hasattr(app, "_review_tab") and app._review_tab.winfo_exists():
            app.doc_nb.select(app._review_tab)
            return
        app._review_tab = app._new_tab("Review")
        self.review_window = ReviewToolbox(app._review_tab, app)
        self.review_window.pack(fill=tk.BOTH, expand=True)

    def send_review_email(self, review):
        recipients = [
            p.email for p in review.participants if p.role == "reviewer" and p.email
        ]
        if not recipients:
            return
        current_email = next(
            (p.email for p in review.participants if p.name == self.app.current_user),
            None,
        )
        if current_email and current_email not in recipients:
            recipients.append(current_email)
        subject = f"Review: {review.name}"
        lines = [f"Review Name: {review.name}", f"Description: {review.description}", ""]
        if review.fta_ids:
            lines.append("FTA IDs:")
            for tid in review.fta_ids:
                lines.append(f" - {tid}")
        if review.fmea_names:
            lines.append("FMEA Names:")
            for name in review.fmea_names:
                lines.append(f" - {name}")
        if getattr(review, "hazop_names", []):
            lines.append("HAZOP Names:")
            for name in review.hazop_names:
                lines.append(f" - {name}")
        if getattr(review, "hara_names", []):
            lines.append("HARA Names:")
            for name in review.hara_names:
                lines.append(f" - {name}")
        msg = "\n".join(lines)
        try:
            self.app.user_manager.send_email(subject, msg, recipients)
        except Exception as e:  # pragma: no cover
            messagebox.showerror("Email", f"Failed to send review email: {e}")

    def review_is_closed(self):
        return self.review_is_closed_for(self.review_data)

    def review_is_closed_for(self, review):
        if not review:
            return False
        if getattr(review, "closed", False):
            return True
        if review.due_date:
            try:
                due = datetime.datetime.strptime(review.due_date, "%Y-%m-%d").date()
                return datetime.date.today() > due
            except ValueError:
                return False
        return False

    def get_requirements_for_review(self, review):
        ids = set()
        for tid in getattr(review, "fta_ids", []):
            ids.add(tid)
        for name in getattr(review, "fmea_names", []):
            ids.add(name)
        return ids

    def merge_review_comments(self):
        path = filedialog.askopenfilename(
            defaultextension=".json", filetypes=[("JSON", "*.json")]
        )
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
            review = next(
                (r for r in self.reviews if r.name == rd.get("name", "")),
                None,
            )
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

    # ------------------------------------------------------------------
    # Version comparison
    # ------------------------------------------------------------------
    def compare_versions(self):
        if not self.versions:
            messagebox.showinfo("Versions", "No previous versions")
            return
        app = self.app
        if hasattr(app, "_compare_tab") and app._compare_tab.winfo_exists():
            app.doc_nb.select(app._compare_tab)
            return
        app._compare_tab = app._new_tab("Compare")
        dlg = VersionCompareDialog(app._compare_tab, app)
        dlg.pack(fill=tk.BOTH, expand=True)

    def calculate_diff_nodes(self, old_data):
        old_map = self.node_map_from_data(old_data["top_events"])
        new_map = self.node_map_from_data([e.to_dict() for e in self.app.top_events])
        changed = []
        for nid, nd in new_map.items():
            if nid not in old_map:
                changed.append(nid)
            elif json.dumps(old_map[nid], sort_keys=True) != json.dumps(
                nd, sort_keys=True
            ):
                changed.append(nid)
        return changed

    def calculate_diff_between(self, data1, data2):
        map1 = self.node_map_from_data(data1["top_events"])
        map2 = self.node_map_from_data(data2["top_events"])
        changed = []
        for nid, nd in map2.items():
            if nid not in map1 or json.dumps(map1.get(nid, {}), sort_keys=True) != json.dumps(
                nd, sort_keys=True
            ):
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

    def get_review_targets(self):
        targets = []
        target_map = {}
        if self.review_data:
            allowed_ftas = set(self.review_data.fta_ids)
            allowed_fmeas = set(self.review_data.fmea_names)
            allowed_fmedas = set(getattr(self.review_data, "fmeda_names", []))
        else:
            allowed_ftas = set()
            allowed_fmeas = set()
            allowed_fmedas = set()
        nodes = []
        if allowed_ftas:
            for te in self.app.top_events:
                if te.unique_id in allowed_ftas:
                    nodes.append(te)
        else:
            nodes.extend(self.app.top_events)
        if allowed_fmeas:
            for f in self.app.fmeas:
                if f.name in allowed_fmeas:
                    nodes.append(f)
        else:
            nodes.extend(self.app.fmeas)
        if allowed_fmedas:
            for d in getattr(self.app, "fmedas", []):
                if d.name in allowed_fmedas:
                    nodes.append(d)
        else:
            nodes.extend(getattr(self.app, "fmedas", []))
        for node in nodes:
            targets.append(node)
            target_map[getattr(node, "unique_id", getattr(node, "name", None))] = node
        return targets, target_map

    @property
    def joint_reviews(self):
        return [r for r in self.reviews if getattr(r, "mode", "") == "joint"]
