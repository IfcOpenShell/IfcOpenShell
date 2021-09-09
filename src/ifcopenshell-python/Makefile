.PHONY: test
test:
	pytest -p no:pytest-blender test

.PHONY: qa
qa:
	black .

.PHONY: coverage
coverage:
	coverage run --source ifcopenshell -m pytest
	coverage html
	xdg-open htmlcov/index.html

.PHONY: clean
clean:
	rm -rf htmlcov
