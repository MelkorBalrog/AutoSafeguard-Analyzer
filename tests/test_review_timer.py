import time
import unittest
import tkinter as tk
from gui.review_toolbox import ReviewParticipant, ReviewData, ReviewToolbox


class ReviewTimerTests(unittest.TestCase):
    def test_mark_done_records_time(self):
        try:
            root = tk.Tk()
            root.withdraw()
        except tk.TclError:
            self.skipTest("Tk not available")

        class StubApp:
            def __init__(self):
                self.current_user = "alice"
                self.review_data = ReviewData(participants=[ReviewParticipant("alice", "a@x", "reviewer")])
                self.reviews = []
                self.comment_target = None
                self.selected_node = None

            def update_hara_statuses(self):
                pass

            def review_is_closed(self):
                return False

            def find_node_by_id_all(self, _):
                return None

            def focus_on_node(self, _):
                pass

            def get_review_targets(self):
                return [], {}

        app = StubApp()
        toolbox = ReviewToolbox(root, app)
        toolbox.start_participant_timer()
        time.sleep(0.01)
        toolbox.mark_done()
        p = app.review_data.participants[0]
        self.assertTrue(p.done)
        self.assertGreater(p.time_spent, 0)
        root.destroy()


if __name__ == "__main__":
    unittest.main()
