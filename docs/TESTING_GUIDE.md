# Testing Guide

Run commands from the repository root.

## Install dependencies
```powershell
py -m pip install -r requirements.txt
```

## Run the test suite
```powershell
py -m unittest discover -s tests -v
```

If the project uses pytest in your environment, you can also run:
```powershell
py -m pytest -q
```

## Contribution checklist
- Add tests for new behavior and invalid inputs.
- Run relevant tests before committing.
- Keep commits focused on one change.
- Avoid committing secrets, local environments, or generated datasets.
- Verify `git status` before pushing.
