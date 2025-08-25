# Author: Miguel Marina <karel.capek.robotics@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2025 Capek System Safety & Robotic Solutions
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
