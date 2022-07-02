.PHONY: test
test:
	pytest -p no:pytest-blender test

.PHONY: build-ids-docs
build-ids-docs:
	mkdir -p test/build
	cd test && python ids_doc_generator.py

.PHONY: qa
qa:
	black .
	pylint ./* --output-format=colorized --disable all --enable E

.PHONY: license
license:
	#copyright-header --license LGPL3 --copyright-holder "Thomas Krijnen <thomas@aecgeeks.com>" --copyright-year "2022" --copyright-software "IfcOpenShell" --copyright-software-description "IFC toolkit and geometry engine" -a ./ -o ./
	copyright-header --license LGPL3 --copyright-holder "Dion Moult <dion@thinkmoult.com>" --copyright-year "2022" --copyright-software "IfcOpenShell" --copyright-software-description "IFC toolkit and geometry engine" -a ./ -o ./

.PHONY: coverage
coverage:
	coverage run --source ifcopenshell -m pytest -p no:pytest-blender test
	coverage html
	xdg-open htmlcov/index.html

.PHONY: clean
clean:
	rm -rf htmlcov
