## Setup

Mandown requires Python 3.10+ and [poetry](https://python-poetry.org):

```
pip install poetry
```

Install dependencies:

```bash
poetry install
poetry install -E postprocessing  # image processing
poetry install -E gui  # Qt GUI
```

To run the main CLI project:

```
poetry run mandown <FLAGS>
```

For the Qt GUI:

```
poetry run mandown-gui
```

## Development

Please ensure that code is properly formatted prior to pushes via the pre-commit tool:

```
pip install pre-commit
```

Ensure that formatting is checked before commit:

```
pre-commit install
```

Run unit tests:

```
poetry run pytest
```
