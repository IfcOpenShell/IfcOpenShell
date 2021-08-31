.PHONY: test
test:
	cd test && pytest

.PHONY: coverage
coverage:
	coverage run --source ifcopenshell -m pytest
	coverage html
	xdg-open htmlcov/index.html

.PHONY: clean
clean:
	rm -rf htmlcov
