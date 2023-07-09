#!/usr/bin/env bash
vi src/json_to_csv_filter/__init__.py
python3 -m build
python3 -m twine upload dist/*