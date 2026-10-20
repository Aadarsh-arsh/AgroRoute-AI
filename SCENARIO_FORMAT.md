# Farm Scenario Format

AgroRoute-AI represents a farm as a rectangular grid.

## Supported cell types
- `empty`: traversable empty space.
- `crop`: a crop location.
- `obstacle`: a blocked location.
- `infected`: a marked infected zone.

## Scenario fields
The Farm model exports `schema_version`, `name`, `rows`, `cols`,
`cells`, `rover`, and `severities` through `Farm.to_dict()`.

Coordinates are zero-based. The rover position is represented as a
row-column pair. Severity keys use the format `row,col`.

The current schema version is 1. Use `Farm.from_dict()` to validate
and reconstruct scenarios instead of duplicating model validation.
