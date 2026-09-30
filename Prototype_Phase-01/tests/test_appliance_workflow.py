"""Execute 7.4 as separate page sessions with the original CSV and real sklearn.

Set APPLIANCE_CSV to a downloaded energydata_complete.csv to enable this test.
Only the browser's open_url transport is replaced; all authored steps run as-is.
"""
import contextlib
import io
import os
from pathlib import Path
import re
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.environ.get("APPLIANCE_CSV"), "Set APPLIANCE_CSV to the original dataset")
class ApplianceWorkflow(unittest.TestCase):
    def test_each_page_runs_in_a_fresh_namespace(self):
        import numpy as np
        csv = Path(os.environ["APPLIANCE_CSV"]).read_text()
        http = types.ModuleType("pyodide.http")
        def open_url(url):
            self.assertEqual(url, "https://raw.githubusercontent.com/LuisM78/"
                             "Appliances-energy-prediction-data/master/energydata_complete.csv")
            return io.StringIO(csv)
        http.open_url = open_url
        source = (ROOT / "content/deep-learning/7.4-appliance-energy-demo.md").read_text()
        labs = re.findall(r":::pylab[^\n]*\n(.*?)\n:::", source, re.S)
        self.assertEqual(len(labs), 5)
        sessions = []
        with patch.dict(sys.modules, {"pyodide": types.ModuleType("pyodide"), "pyodide.http": http}):
            for page, lab in enumerate(labs, 2):
                with self.subTest(page=page):
                    namespace = {}
                    steps = re.split(r"^# step: .+$", lab, flags=re.M)[1:]
                    with contextlib.redirect_stdout(io.StringIO()):
                        for step in steps:
                            exec(compile(step, f"7.4 page {page}", "exec"), namespace)
                    self.assertEqual(namespace["df"].shape[0], 4934)
                    if page >= 3:
                        self.assertEqual(len(namespace["y_tr"]), 3947)
                        self.assertEqual(len(namespace["y_te"]), 987)
                        np.testing.assert_array_equal(namespace["y_te"], sessions[1]["y_te"] if len(sessions) > 1 else namespace["y_te"])
                    if page >= 4:
                        np.testing.assert_allclose(namespace["scaler"].mean_, namespace["X_tr"].mean(axis=0))
                        pred = namespace["scaled"].predict(namespace["Xs_te"])
                        self.assertTrue(np.isfinite(pred).all())
                        if page > 4:
                            reference = sessions[2]
                            np.testing.assert_allclose(pred, reference["scaled"].predict(reference["Xs_te"]))
                    sessions.append(namespace)
        self.assertEqual(len(sessions[3]["s"]), len(sessions[3]["features"]))
        self.assertTrue({"rv1", "rv2"}.issubset(sessions[3]["s"].index))
        last = sessions[-1]
        predictions = last["m2"].predict(last["sc2"].transform(last["Xte2"]))
        self.assertTrue(np.isfinite(predictions).all())
        self.assertLess(last["df"].date.iloc[last["cut"] - 1], last["df"].date.iloc[last["cut"]])


if __name__ == "__main__":
    unittest.main()
