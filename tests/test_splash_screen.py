import unittest
import tkinter as tk

from gui.splash_screen import SplashScreen


class SplashScreenTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk not available")
        self.root.withdraw()
        self.splash = SplashScreen(self.root, duration=0)

    def tearDown(self):
        try:
            self.splash.destroy()
        finally:
            self.root.destroy()

    def test_gear_has_glow(self):
        self.splash._draw_gear()
        glow_items = self.splash.canvas.find_withtag("gear_glow")
        self.assertGreater(len(glow_items), 0)
        gear_items = self.splash.canvas.find_withtag("gear")
        self.assertEqual(len(gear_items), 1)

    def test_title_background(self):
        bg_items = self.splash.canvas.find_withtag("title_bg")
        text_items = self.splash.canvas.find_withtag("title_text")
        self.assertEqual(len(bg_items), 1)
        self.assertEqual(len(text_items), 2)
        self.assertEqual(self.splash.canvas.itemcget(bg_items[0], "fill"), "black")
        for t in text_items:
            self.assertEqual(self.splash.canvas.itemcget(t, "fill"), "white")


if __name__ == "__main__":
    unittest.main()
