.PHONY: backend-test frontend-test frontend-build lint format-check check

backend-test:
	cd backend && python3 -m pytest

frontend-test:
	cd frontend && npm test -- --run

frontend-build:
	cd frontend && npm run build

lint: format-check

format-check:
	git diff --check

check: backend-test frontend-test frontend-build format-check
