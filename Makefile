.PHONY: dev lint complex coverage pre-commit yapf sort deploy destroy deps unit infra-tests integration e2e coverage-tests docs lint-docs build format
CWD := $(shell pwd)

.ONESHELL:  # run all commands in a single shell, ensuring it runs within a local virtual env
dev:
	python3 -m venv .venv
	. .venv/bin/activate
	pip install --upgrade pip pre-commit poetry
	pre-commit install
	poetry config --local virtualenvs.in-project true
	poetry install
	npm ci

format:
	isort $(CWD)
	yapf -d -vv --style=./.style -r .

lint: format
	@echo "Running flake8"
	flake8 product/* infrastructure/* tests/*
	@echo "Running mypy"
	$(MAKE) mypy-lint

complex:
	@echo "Running Radon"
	radon cc -e 'tests/*,cdk.out/*' .
	@echo "Running xenon"
	xenon --max-absolute B --max-modules A --max-average A -e 'tests/*,.venv/*,cdk.out/*' .

pre-commit:
	pre-commit run -a --show-diff-on-failure

mypy-lint:
	mypy --pretty product infrastructure tests

deps:
	poetry export --only=dev --format=requirements.txt > dev_requirements.txt
	poetry export --without=dev --format=requirements.txt > lambda_requirements.txt

unit:
	pytest tests/unit  --cov-config=.coveragerc --cov=product --cov-report xml

build: deps
	mkdir -p .build/lambdas ; cp -r product .build/lambdas
	mkdir -p .build/common_layer ; poetry export --without=dev --without-hashes --format=requirements.txt > .build/common_layer/requirements.txt

infra-tests: build
	pytest tests/infrastructure

integration:
	pytest tests/integration  --cov-config=.coveragerc --cov=product --cov-report xml

e2e:
	pytest tests/e2e  --cov-config=.coveragerc --cov=product --cov-report xml

pr: deps yapf sort pre-commit complex lint unit deploy integration e2e

yapf:
	yapf -i -vv --style=./.style --exclude=.venv --exclude=.build --exclude=cdk.out --exclude=.git  -r .

coverage-tests:
	pytest tests/unit tests/integration  --cov-config=.coveragerc --cov=product --cov-report xml

deploy: build
	npx cdk deploy --app="python3 ${PWD}/app.py" --require-approval=never

destroy:
	npx cdk destroy --app="python3 ${PWD}/app.py" --force

docs:
	mkdocs serve

lint-docs:
	docker run -v ${PWD}:/markdown 06kellyjac/markdownlint-cli --fix "docs"
