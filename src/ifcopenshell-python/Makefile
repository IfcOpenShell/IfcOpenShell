.PHONY: test
test:
	pytest -p no:pytest-blender test

.PHONY: qa
qa:
	black .
	pylint ./* --output-format=colorized --disable all --enable E

.PHONY: coverage
coverage:
	coverage run --source ifcopenshell -m pytest
	coverage html
	xdg-open htmlcov/index.html

.PHONY: clean
clean:
	rm -rf htmlcov
