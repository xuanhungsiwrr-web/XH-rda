import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "caotrinh_ke", ROOT / "scripts" / "caotrinh_ke.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CaoTrinhKeTests(unittest.TestCase):
    def test_calculation_returns_crest_above_design_level(self):
        result = MODULE.tinh(
            {
                "Htk": 2.33,
                "V50": 31,
                "L": 800,
                "d": 4,
                "tau_on": False,
                "gio_on": False,
                "b": 0.26,
                "sct": 0.10,
                "snen": 0.20,
            }
        )
        self.assertGreater(result["Zd"], result["Htk"])
        self.assertGreaterEqual(result["Zc"], result["Zd"])
        self.assertEqual(result["quyet"], "khong xet")

    def test_yaml_block_contains_traceable_inputs(self):
        result = MODULE.tinh({"Htk": 2.0, "V50": 20, "L": 500, "d": 3})
        rendered = MODULE.yaml_block(result)
        self.assertIn("Htk:", rendered)
        self.assertIn("Zc_thiet_ke:", rendered)

    def test_invalid_input_is_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.tinh({"Htk": 2.0, "V50": 20, "L": 500, "d": 3, "cap": "invalid"})


if __name__ == "__main__":
    unittest.main()
