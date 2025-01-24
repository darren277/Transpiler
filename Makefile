.ONESHELL:

activate:
	.\venv\Scripts\activate

jsx-install:
	cd tests/testout/jsx && npm install

test: activate
	python tests/basics.py

test-jsx: activate
	python tests/jsx_tests.py


test:
	pytest

cov:
	pytest --cov=. --cov-report=term-missing
