COMPOSE_DEV = docker compose -f compose.dev.yaml

.PHONY: dev dev-down dev-logs dev-migrate migrate

dev:
	$(COMPOSE_DEV) up --build

dev-down:
	$(COMPOSE_DEV) down

dev-logs:
	$(COMPOSE_DEV) logs -f

dev-migrate:
	$(COMPOSE_DEV) exec api uv run --no-sync alembic upgrade head

migrate:
	uv run --no-sync alembic upgrade head
