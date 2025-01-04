#!/bin/bash

cd /app/workspace

# poetry config http-basic.polynom-packages $POLYNOM_PRIVATE_PYPI_USERNAME $POLYNOM_PRIVATE_PYPI_PASSWORD
poetry install --with dev
poetry run pre-commit install -f --hook-type pre-commit
poetry run pre-commit autoupdate

echo "###### READY TO ROCK !"
