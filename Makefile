# Prérequis : uv (https://docs.astral.sh/uv/)
UV ?= uv

setup:
	$(UV) sync --locked --all-extras

test:             ## 8 tests : actualisation à la main, DCF inversé, Gordon, sensibilité, chargeur (sans réseau)
	$(UV) run pytest

lint:
	$(UV) run ruff check src tests

build:            ## 4 tables, 3 figures, classeur Excel (exige `vlab fetch` d'abord)
	$(UV) run vlab build
