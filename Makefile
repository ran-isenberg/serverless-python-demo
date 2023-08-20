.PHONY: dev lint complex coverage pre-commit yapf sort deploy destroy deps unit infra-tests integration e2e coverage-tests docs lint-docs build format
CWD := $(shell pwd)

.ONESHELL:  # run all commands in a single shell, ensuring it runs within a local virtual env
dev:
	pip install --upgrade pip pre-commit poetry
	pre-commit install
# ensures poetry creates a local virtualenv (.venv)
	poetry config --local virtualenvs.in-project true
	poetry install
	npm ci

format:
	poetry run isort $(CWD)
	poetry run yapf -d -vv --style=./.style -r .

lint: format
	@echo "Running flake8"
	poetry run flake8 product/* infrastructure/* tests/*
	@echo "Running mypy"
	$(MAKE) mypy-lint

complex:
	@echo "Running Radon"
	poetry run radon cc -e 'tests/*,cdk.out/*' .
	@echo "Running xenon"
	poetry run xenon --max-absolute B --max-modules A --max-average A -e 'tests/*,.venv/*,cdk.out/*' .

pre-commit:
	poetry run pre-commit run -a --show-diff-on-failure

mypy-lint:
	poetry run mypy --pretty product infrastructure tests

deps:
	poetry export --only=dev --format=requirements.txt > dev_requirements.txt
	poetry export --without=dev --format=requirements.txt > lambda_requirements.txt

unit:
	poetry run pytest tests/unit  --cov-config=.coveragerc --cov=product --cov-report xml

build: deps
	mkdir -p .build/lambdas ; cp -r product .build/lambdas
	mkdir -p .build/common_layer ; poetry export --without=dev --without-hashes --format=requirements.txt > .build/common_layer/requirements.txt

infra-tests: build
	poetry run pytest tests/infrastructure

integration:
	poetry run pytest tests/integration  --cov-config=.coveragerc --cov=product --cov-report xml

e2e:
	poetry run pytest tests/e2e  --cov-config=.coveragerc --cov=product --cov-report xml

pr: deps yapf sort pre-commit complex lint unit deploy integration e2e

coverage-tests:
	poetry run pytest tests/unit tests/integration  --cov-config=.coveragerc --cov=product --cov-report xml

deploy: build
	npx cdk deploy --app="python3 ${PWD}/app.py" --require-approval=never

destroy:
	npx cdk destroy --app="python3 ${PWD}/app.py" --force

docs:
	poetry run mkdocs serve

lint-docs:
	docker run -v ${PWD}:/markdown 06kellyjac/markdownlint-cli --fix "docs"
