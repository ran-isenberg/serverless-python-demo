.PHONY: dev lint complex coverage pre-commit sort deploy destroy deps unit infra-tests integration ruff e2e coverage-tests docs update-deps lint-docs build format
PYTHON := ".venv/bin/python3"

.ONESHELL:  # run all commands in a single shell, ensuring it runs within a local virtual env
dev:
	pip install --upgrade pip pre-commit poetry
	pre-commit install
# ensures poetry creates a local virtualenv (.venv)
	poetry config --local virtualenvs.in-project true
	poetry install --no-root
	npm ci

format:
	poetry run ruff check . --fix

format-fix:
	poetry run ruff format .

lint: format
	@echo "Running mypy"
	$(MAKE) mypy-lint

complex:
	@echo "Running Radon"
	poetry run radon cc -e 'tests/*,docs/*,cdk.out/*,node_modules/*' .
	@echo "Running xenon"
	poetry run xenon --max-absolute B --max-modules A --max-average A -e 'tests/*,docs/*,.venv/*,cdk.out/*,node_modules/*' .

pre-commit:
	poetry run pre-commit run -a --show-diff-on-failure

mypy-lint:
	poetry run mypy --pretty product infrastructure tests docs/examples/

deps:
	poetry export --only=dev --format=requirements.txt > dev_requirements.txt
	poetry export --without=dev --format=requirements.txt > lambda_requirements.txt

unit:
	poetry run pytest tests/unit  --cov-config=.coveragerc --cov=product --cov-report xml

build: deps
	mkdir -p .build/lambdas ; cp -r product .build/lambdas
	mkdir -p .build/common_layer ; poetry export --without=dev --format=requirements.txt > .build/common_layer/requirements.txt

infra-tests: build
	poetry run pytest tests/infrastructure

integration:
	poetry run pytest tests/integration  --cov-config=.coveragerc --cov=product --cov-report xml

e2e:
	poetry run pytest tests/e2e  --cov-config=.coveragerc --cov=product --cov-report xml

pr: deps format pre-commit complex lint unit deploy integration e2e

coverage-tests:
	poetry run pytest tests/unit tests/integration  --cov-config=.coveragerc --cov=product --cov-report xml

deploy: build
	npx cdk deploy --app="${PYTHON} ${PWD}/app.py" --require-approval=never

destroy:
	npx cdk destroy --app="${PYTHON} ${PWD}/app.py" --force

docs:
	poetry run mkdocs serve

lint-docs:
	docker run -v ${PWD}:/markdown 06kellyjac/markdownlint-cli --fix "docs"

watch:
	npx cdk watch

update-deps:
	poetry update
	pre-commit autoupdate
	npm i --package-lock-only
