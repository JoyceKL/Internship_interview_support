.PHONY: run-api run-ui test migrate seed

run-api:
	uvicorn backend.main:app --reload --port 8000

run-ui:
	streamlit run app.py

test:
	pytest -q

migrate:
	alembic -c backend/alembic.ini upgrade head

seed:
	python -m backend.storage.seed
