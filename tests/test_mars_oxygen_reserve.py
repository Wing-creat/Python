"""Tests for a simple Mars habitat oxygen reserve estimate."""

import sys
import subprocess
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "06_Astronomy"))

from mars_oxygen_budget import simulate_oxygen_budget
from mars_oxygen_reserve import required_starting_stock_kg, save_reserve_plot


class MarsOxygenReserveTests(unittest.TestCase):
    def test_required_starting_stock_accounts_for_pre_outage_gain_and_outage_loss(self):
        required = required_starting_stock_kg(
            target_end_kg=2.0,
            days_before_outage=7,
            outage_days=4,
            production_kg_per_day=4.5,
            use_and_leak_kg_per_day=4.1,
        )
        self.assertAlmostEqual(required, 15.6)

        at_target = simulate_oxygen_budget(
            initial_oxygen_kg=required, days=11,
            outage_day=8, outage_duration_days=4,
        )
        below_target = simulate_oxygen_budget(
            initial_oxygen_kg=15.5, days=11,
            outage_day=8, outage_duration_days=4,
        )
        self.assertAlmostEqual(at_target[-1], 2.0)
        self.assertAlmostEqual(below_target[-1], 1.9)

    def test_plot_creates_a_nonempty_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "mars" / "reserve.png"
            save_reserve_plot(
                [10.0, 14.0, 15.6, 17.0],
                [0.0, 0.4, 2.0, 3.4],
                target_end_kg=2.0,
                required_start_kg=15.6,
                output_path=str(output),
            )
            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 0)

    def test_script_reports_calculation_and_saves_plot(self):
        script = Path(__file__).resolve().parents[1] / "06_Astronomy" / "mars_oxygen_reserve.py"
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(script)], cwd=directory,
                capture_output=True, text=True, check=True,
            )
            self.assertIn("15.6 kg", result.stdout)
            self.assertIn("2.0 kg", result.stdout)
            self.assertTrue((Path(directory) / "assets" / "mars_oxygen_reserve.png").is_file())


if __name__ == "__main__":
    unittest.main()
