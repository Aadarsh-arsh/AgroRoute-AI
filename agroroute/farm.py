"""Validated, portable farm scenario model."""
from __future__ import annotations
from dataclasses import dataclass, field
from copy import deepcopy
from typing import Any

CELL_TYPES = ('empty', 'crop', 'obstacle', 'infected')
SEVERITIES = ('Low', 'Medium', 'High')
MAX_DIMENSION = 30

@dataclass
class Farm:
    rows: int = 12
    cols: int = 12
    cells: list[list[str]] = field(default_factory=list)
    rover: tuple[int, int] = (0, 0)
    severities: dict[str, str] = field(default_factory=dict)
    name: str = 'My Farm'

    def __post_init__(self):
        if not (5 <= self.rows <= MAX_DIMENSION and 5 <= self.cols <= MAX_DIMENSION):
            raise ValueError('Farm dimensions must be between 5 and 30.')
        if not self.cells:
            self.cells = [['crop' for _ in range(self.cols)] for _ in range(self.rows)]
        if len(self.cells) != self.rows or any(len(row) != self.cols for row in self.cells):
            raise ValueError('Cell grid dimensions do not match farm dimensions.')
        if any(cell not in CELL_TYPES for row in self.cells for cell in row):
            raise ValueError('Invalid cell type in grid.')
        if not self.in_bounds(*self.rover):
            raise ValueError('Rover position outside farm.')
        if self.cells[self.rover[0]][self.rover[1]] in ('obstacle', 'infected'):
            raise ValueError('Rover cannot start on obstacle or infected zone.')
        for key, severity in self.severities.items():
            r, c = self.parse_key(key)
            if not self.in_bounds(r, c) or self.cells[r][c] != 'infected' or severity not in SEVERITIES:
                raise ValueError('Invalid infected-zone severity data.')
        self.severities = {self.key(r,c): self.severities.get(self.key(r,c), 'Medium')
                           for r in range(self.rows) for c in range(self.cols)
                           if self.cells[r][c] == 'infected'}

    @staticmethod
    def key(row: int, col: int) -> str:
        return f'{row},{col}'

    @staticmethod
    def parse_key(key: str) -> tuple[int, int]:
        parts = key.split(',')
        if len(parts) != 2:
            raise ValueError('Invalid cell coordinate.')
        return int(parts[0]), int(parts[1])

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def paint(self, row: int, col: int, tool: str, severity: str = 'Medium') -> None:
        if not self.in_bounds(row, col):
            raise ValueError('Cell is outside the farm.')
        if tool == 'rover':
            if self.cells[row][col] in ('obstacle', 'infected'):
                raise ValueError('Move the rover onto a crop or empty cell.')
            self.rover = (row, col)
            return
        if tool not in CELL_TYPES:
            raise ValueError('Unknown painting tool.')
        if (row, col) == self.rover and tool in ('obstacle', 'infected'):
            raise ValueError('Move the rover before placing an obstacle or infected zone here.')
        if tool == 'infected' and severity not in SEVERITIES:
            raise ValueError('Invalid severity.')
        self.cells[row][col] = tool
        key = self.key(row, col)
        self.severities.pop(key, None)
        if tool == 'infected':
            self.severities[key] = severity

    def counts(self) -> dict[str, int]:
        return {kind: sum(cell == kind for row in self.cells for cell in row) for kind in CELL_TYPES}

    def to_dict(self) -> dict[str, Any]:
        return {'schema_version': 1, 'name': self.name, 'rows': self.rows, 'cols': self.cols,
                'cells': self.cells, 'rover': list(self.rover), 'severities': self.severities}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Farm':
        if not isinstance(data, dict) or data.get('schema_version') != 1:
            raise ValueError('Unsupported scenario file format (expected schema_version 1).')
        rover = data['rover']
        if not isinstance(rover, list) or len(rover) != 2 or any(type(x) is not int for x in rover):
            raise ValueError('Invalid rover coordinates.')
        return cls(rows=data['rows'], cols=data['cols'], cells=deepcopy(data['cells']),
                   rover=tuple(rover), severities=deepcopy(data.get('severities', {})), name=str(data.get('name', 'Imported Farm'))[:100])


def demo_farm() -> Farm:
    farm = Farm(name='Demo Tomato Field')
    for r, c in [(3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (7, 6), (7, 7), (9, 2)]:
        farm.paint(r, c, 'obstacle')
    for r, c, severity in [(2, 2, 'High'), (2, 9, 'Medium'), (8, 9, 'Low'), (10, 4, 'High')]:
        farm.paint(r, c, 'infected', severity)
    return farm
