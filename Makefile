PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip
PY := $(VENV)/bin/python
FILE := main.py
MAP := map.txt

.PHONY: install run debug clean lint lint-strict

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	touch $(VENV)/bin/activate

venv: $(VENV)/bin/activate

install: venv
	$(PIP) install -r fly_in/requirements.txt

run: venv
	@$(PY) $(FILE) $(MAP)

debug: venv
	$(PY) -m pdb $(FILE)

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	rm -rf dist build *.egg-info
	find . -name "*.pyc" -delete

lint: venv
	$(PY) -m flake8 .
	$(PY) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: venv
	$(PY) -m flake8 .
	$(PY) -m mypy . --strict

build: venv
	$(PY) -m build --outdir .
	rm -rf *.egg-info