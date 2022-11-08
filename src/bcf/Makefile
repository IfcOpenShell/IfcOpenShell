.PHONY: test
test:
	tox

.PHONY: qa
qa:
	black .
	isort .
	pylint ./src --output-format=colorized

.PHONY: typecheck
typecheck:
	mypy src/bcf

.PHONY: license
license:
	copyright-header --license LGPL3 --copyright-holder "Andrea Ghensi <andrea.ghensi@gmail.com>" --copyright-year "2022" --copyright-software "IfcOpenShell" --copyright-software-description "BCF XML file handling" -a ./ -o ./

.PHONY: coverage
coverage:
	coverage run --source bcf -m pytest tests
	coverage html
	xdg-open htmlcov/index.html

.PHONY: clean
clean:
	rm -rf htmlcov

# TODO: make this based on xsd file presence
.PHONY: models
models:
	cd src && xsdata generate -p bcf.v2.model --unnest-classes --kw-only --slots -ds Google bcf/v2/xsd
	cd src && xsdata generate -p bcf.v3.model --unnest-classes --kw-only --slots -ds Google bcf/v3/xsd

# .PHONY
# api:
#     openapi-python-client generate --url https://api.swaggerhub.com/apis/buildingSMART/BCF/3.0
