.PHONY: setup preflight preflight-ps run-api run-ui test migrate migrate-docker seed seed-docker run

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt
	cp -n .env.example .env || true
	mkdir -p data/uploads/cv data/uploads/jd data/exports

preflight:
	bash scripts/preflight.sh

preflight-ps:
	powershell -ExecutionPolicy Bypass -File scripts/preflight.ps1

run-api:
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

run: run-api

run-ui:
	streamlit run app.py

test:
	pytest -q

migrate:
	alembic -c backend/alembic.ini upgrade head

migrate-docker:
	docker compose exec api alembic -c backend/alembic.ini upgrade head

seed:
	python -m backend.storage.seed

seed-docker:
	docker compose exec api python -m backend.storage.seed
