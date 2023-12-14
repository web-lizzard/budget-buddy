.PHONY: *

BACKEND_RUN := @docker compose run --rm backend
FRONTEND_RUN := @docker compose run --rm frontend

DEPENDENCY ?= $(shell bash -c 'read -p "Dependency: " dependency; echo $$dependency')
MESSAGE ?= $(shell bash -c 'read -p "Message: " message; echo $$message')


# common

build: # build docker image
	@docker compose --progress plain build

up: # start docker containers
	@docker compose up

prune: # remove unused docker resources
	@docker system prune --all


# backend

enter_backend: # enter container
	$(BACKEND_RUN) bash


pytest: # run tests
	$(BACKEND_RUN) pytest


poetry_add: # add dependency
	$(BACKEND_RUN) poetry add "$(DEPENDENCY)"

poetry_add_dev: # add dev dependency
	$(BACKEND_RUN) poetry add "$(DEPENDENCY)" -G dev

poetry_remove: # remove dependency
	$(BACKEND_RUN) poetry remove "$(DEPENDENCY)"

poetry_show: # print dependency tree
	$(BACKEND_RUN) poetry show --tree

poetry_lock: # regenerate lock file
	$(BACKEND_RUN) poetry lock --no-update


alembic_revision: # add new database migration
	$(BACKEND_RUN) alembic revision --autogenerate -m "$(MESSAGE)"

alembic_upgrade: # apply database migrations
	$(BACKEND_RUN) alembic upgrade head

alembic_downgrade: # revert last database migration
	$(BACKEND_RUN) alembic downgrade -1
