import json
import tempfile
import unittest
from pathlib import Path

from agroroute.farm import Farm
from agroroute.scenario_io import load_scenario, save_scenario


class ScenarioIOTests(unittest.TestCase):
    def test_scenario_round_trip(self):
        farm = Farm(rows=5, cols=5)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "farm.json"
            save_scenario(farm, path)
            loaded = load_scenario(path)

        self.assertEqual(loaded.to_dict(), farm.to_dict())

    def test_save_creates_missing_parent_directories(self):
        farm = Farm(rows=5, cols=5)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "farm.json"
            save_scenario(farm, path)

            self.assertTrue(path.is_file())
            self.assertEqual(load_scenario(path).to_dict(), farm.to_dict())

    def test_invalid_json_raises_value_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_text("{not valid json", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Invalid scenario JSON"):
                load_scenario(path)

    def test_non_object_json_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "array.json"
            path.write_text(json.dumps([]), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "expected a JSON object"):
                load_scenario(path)

    def test_unknown_schema_version_is_rejected(self):
        farm = Farm(rows=5, cols=5)
        data = farm.to_dict()
        data["schema_version"] = 999

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "future-schema.json"
            path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_scenario(path)


if __name__ == "__main__":
    unittest.main()
