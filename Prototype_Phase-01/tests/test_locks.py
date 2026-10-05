"""The student build keeps locked modules locked: no lesson content, no links, no search entries."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class LockedModules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.course = yaml.safe_load((ROOT / "course.yml").read_text(encoding="utf-8"))
        cls.locked = [m for m in cls.course["modules"] if m.get("locked")]
        cls.tmp = tempfile.TemporaryDirectory()
        cls.site = Path(cls.tmp.name) / "site"
        subprocess.run([sys.executable, str(ROOT / "engine" / "build.py"), "--out", str(cls.site)],
                       check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_locked_lessons_show_only_the_lock_notice(self):
        if not self.locked:
            self.skipTest("no module is locked")
        for mod in self.locked:
            for rel in mod["episodes"]:
                ep = Path(rel).name.split("-")[0].replace(".", "-")
                page = (self.site / f"{ep}-index.html").read_text(encoding="utf-8")
                self.assertIn("This lesson is temporarily locked", page, rel)
                self.assertNotIn('class="pylab"', page, rel)

    def test_locked_lessons_are_not_linked_or_searchable(self):
        if not self.locked:
            self.skipTest("no module is locked")
        index = json.loads((self.site / "search.json").read_text(encoding="utf-8"))
        locked_eps = {Path(rel).name.split("-")[0] for m in self.locked for rel in m["episodes"]}
        self.assertFalse([e for e in index if e.get("e") in locked_eps])
        modules = (self.site / "modules.html").read_text(encoding="utf-8")
        for ep in locked_eps:
            self.assertNotIn(f'href="{ep.replace(".", "-")}-index.html"', modules, ep)


if __name__ == "__main__":
    unittest.main()
