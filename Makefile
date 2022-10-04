.ONESHELL:

activate:
	.\venv\Scripts\activate

test: activate
	python tests/basics.py
