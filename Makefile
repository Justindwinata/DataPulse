.PHONY: backend-test frontend-test frontend-build format-check check

backend-test:
	cd backend && python3 -m pytest

frontend-test:
	cd frontend && npm test -- --run

frontend-build:
	cd frontend && npm run build

format-check:
	git diff --check

check: backend-test frontend-test frontend-build format-check
