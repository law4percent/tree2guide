# Installation

## Requirements

- Python 3.9 or later
- No other dependencies

## Install from PyPI

```bash
pip install tree2guide
```

This installs the `tree2guide` command directly on your PATH. No `python` prefix needed:

```bash
tree2guide docs
```

## Install from source (contributors)

If you're working on `tree2guide` itself, install into a virtual environment to keep things isolated:

### macOS / Linux

```bash
git clone https://github.com/law4percent/tree2guide.git
cd tree2guide/tree2guide_pkg
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Windows

```bat
git clone https://github.com/law4percent/tree2guide.git
cd tree2guide\tree2guide_pkg
python -m venv venv
venv\Scripts\activate
pip install -e ".[dev]"
```

Once activated, both `tree2guide` and `pytest` work normally:

```bash
tree2guide . --stdout
pytest
```

## Re-activating the venv later

Each time you return to the project in a new terminal:

```bash
# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

## Uninstalling

```bash
pip uninstall tree2guide
```

To remove it from a virtual environment, just delete the `venv/` folder:

```bash
# macOS / Linux
rm -rf venv

# Windows
rmdir /s /q venv
```

## Verify the install

```bash
tree2guide --help
```

You should see the full usage message. If you get `command not found`, check that your Python's `bin/` (or `Scripts/` on Windows) is on your PATH.