.PHONY: install test

install:
	pip install .

test: install
	zoinks ./zoinks/examples/