"""Regression checks for charts and the shared UI contract (no Streamlit server needed)."""
import unittest
from pathlib import Path

from agroroute.farm import demo_farm, Farm
from agroroute.visualization import farm_figure, SEVERITY_COLOR
from agroroute.pathfinding import search


ROOT = Path(__file__).resolve().parents[1]


class TestPremiumVisuals(unittest.TestCase):
    def test_chart_bounds_only_show_valid_field(self):
        farm = demo_farm()
        fig = farm_figure(farm)
        self.assertEqual(tuple(fig.layout.xaxis.range), (0.5, farm.cols + 0.5))
        self.assertEqual(tuple(fig.layout.yaxis.range), (farm.rows + 0.5, 0.5))
        self.assertTrue(fig.layout.xaxis.fixedrange)
        self.assertTrue(fig.layout.yaxis.fixedrange)
        self.assertTrue(all(1 <= x <= farm.cols for x in fig.layout.xaxis.tickvals))
        self.assertTrue(all(1 <= y <= farm.rows for y in fig.layout.yaxis.tickvals))

    def test_chart_severity_legend(self):
        fig = farm_figure(demo_farm())
        names = {trace.name for trace in fig.data}
        self.assertTrue({'High severity', 'Medium severity', 'Low severity', 'Rover start'} <= names)
        for severity, color in SEVERITY_COLOR.items():
            trace = next(x for x in fig.data if x.name == f'{severity} severity')
            self.assertEqual(trace.marker.color, color)

    def test_path_overlays_are_preserved(self):
        farm = demo_farm()
        result = search(farm, (2, 2), 'A*')
        fig = farm_figure(farm, result)
        self.assertTrue(result.found)
        self.assertIn('Calculated path', [trace.name for trace in fig.data])
        self.assertIn('Destination', [trace.name for trace in fig.data])

    def test_non_square_farm_has_no_invalid_ticks(self):
        farm = Farm(rows=5, cols=30)
        fig = farm_figure(farm)
        self.assertEqual(fig.layout.xaxis.range[-1], 30.5)
        self.assertEqual(fig.layout.yaxis.range[0], 5.5)
        self.assertGreater(len(fig.layout.xaxis.tickvals), 5)

    def test_all_pages_use_same_design_system(self):
        self.assertTrue((ROOT / '.streamlit/config.toml').exists())
        pages = [ROOT / 'app.py', *sorted((ROOT / 'pages').glob('*.py'))]
        self.assertEqual(len(pages), 11)
        for page in pages:
            data = page.read_text(encoding='utf-8')
            with self.subTest(page=page.name):
                self.assertIn('apply_theme()', data)
                self.assertIn('footer()', data)


if __name__ == '__main__':
    unittest.main()
