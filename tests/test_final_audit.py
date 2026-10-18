"""Final regression suite for cross-page state and rover safety invariants."""
import ast
import unittest
from pathlib import Path
from agroroute.farm import Farm, demo_farm
from agroroute.mission_control import preflight
from agroroute.rover import RoverState
from agroroute.autonomous import build_workflow, simulate_to_completion, start_rover, workflow_report

ROOT = Path(__file__).resolve().parents[1]

class TestFinalAudit(unittest.TestCase):
    def test_all_twelve_pages_have_shared_theme(self):
        pages = [ROOT/'app.py', *sorted((ROOT/'pages').glob('*.py'))]
        self.assertEqual(len(pages), 12)
        for file in pages:
            with self.subTest(page=file.name):
                tree = ast.parse(file.read_text(encoding='utf-8'))
                self.assertTrue(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'apply_theme' for n in ast.walk(tree)))
                self.assertTrue(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'set_page_config' for n in ast.walk(tree)))

    def test_scenario_import_does_not_alias_original(self):
        farm = demo_farm()
        raw = farm.to_dict()
        restored = Farm.from_dict(raw)
        restored.paint(1,1,'infected','High')
        self.assertEqual(raw['cells'][1][1],'crop')
        self.assertNotIn('1,1',raw['severities'])

    def test_rover_stops_before_exceeding_inspection_capacity(self):
        farm = Farm(rows=5,cols=5)
        farm.paint(0,1,'infected')
        rover = RoverState([(0,0),(0,1),(0,0)],capacity=0)
        self.assertFalse(rover.tick(farm))
        self.assertEqual(rover.position,(0,0))
        self.assertEqual(rover.step,0)
        self.assertEqual(rover.battery,100)
        self.assertEqual(rover.status,'Inspection capacity reached')

    def test_terminal_rover_cannot_resume(self):
        farm=Farm(rows=5,cols=5)
        rover=RoverState([(0,0),(0,1)])
        self.assertTrue(rover.tick(farm))
        self.assertEqual(rover.status,'Completed')
        self.assertFalse(rover.tick(farm))
        self.assertEqual(rover.step,1)

    def test_invalid_rover_battery_rate(self):
        with self.assertRaises(ValueError):
            RoverState([(0,0),(0,1)]).tick(Farm(rows=5,cols=5),-0.5)

    def test_preflight_out_of_bounds_leg(self):
        farm=Farm(rows=5,cols=5)
        check=preflight(farm,[(0,0),(-1,0),(0,0)],0.4,20)
        self.assertFalse(check.feasible)
        self.assertTrue(any('invalid movement' in issue for issue in check.issues))

    def test_preflight_nan_rejected(self):
        with self.assertRaises(ValueError):
            preflight(Farm(rows=5,cols=5),[(0,0)],float('nan'),20)

    def test_workflow_rejects_changed_capacity(self):
        result=build_workflow(demo_farm(),planner='Nearest Neighbor')
        with self.assertRaises(ValueError):
            start_rover(result,result.capacity-1)

    def test_workflow_rejects_changed_battery_rate(self):
        result=build_workflow(demo_farm(),planner='Nearest Neighbor')
        with self.assertRaises(ValueError):
            simulate_to_completion(result,1.5,result.capacity)

    def test_report_includes_checked_settings(self):
        result=build_workflow(demo_farm(),planner='Nearest Neighbor',reserve=20,capacity=5)
        report=workflow_report(result)
        self.assertEqual(report['inspection_capacity'],5)
        self.assertEqual(report['required_reserve_pct'],20)

    def test_navigation_transfers_safety_settings(self):
        for filename in ('1_Smart_Dashboard.py','11_Autonomous_Workflow.py'):
            with self.subTest(filename=filename):
                text=(ROOT/'pages'/filename).read_text()
                self.assertIn('rover_transfer_settings',text)
                self.assertIn('rover_mission_settings',text)

    def test_stale_diagnoses_reset_on_farm_replacement(self):
        source=(ROOT/'app.py').read_text()
        self.assertGreaterEqual(source.count('st.session_state.zone_diagnoses = {}'),3)
        self.assertIn(".pop(farm.key(r,c), None)",source)

if __name__ == '__main__':
    unittest.main()
