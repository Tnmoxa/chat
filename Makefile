#!make
PYTHON_EXEC ?= python3.11
VENV ?= "./.venv"
SHELL := /bin/bash

default:
	@echo OK

update-venv:
	source $(VENV)/bin/activate && pip install -e .

venv:
	[ -d $(VENV) ] || $(PYTHON_EXEC) -m venv $(VENV)
	source $(VENV)/bin/activate && pip install -U pip wheel setuptools pip-tools
	$(MAKE) update-venv