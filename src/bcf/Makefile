VERSION:=`date '+%y%m%d'`
SED:=sed -i
ifeq ($(UNAME_S),Darwin)
SED:=sed -i '' -e
endif

.PHONY: ci
ci:
	tox

.PHONY: license
license:
	copyright-header --license LGPL3 --copyright-holder "Andrea Ghensi <andrea.ghensi@gmail.com>" --copyright-year "2022" --copyright-software "IfcOpenShell" --copyright-software-description "BCF XML file handling" -a ./ -o ./

# TODO: make this based on xsd file presence
.PHONY: models
models:
	cd src && xsdata generate -p bcf.v2.model --unnest-classes --kw-only --slots -ds Google bcf/v2/xsd
	cd src && xsdata generate -p bcf.v3.model --unnest-classes --kw-only --slots -ds Google bcf/v3/xsd

.PHONY: dist
dist:
	rm -rf dist
	$(SED) "s/999999/$(VERSION)/" pyproject.toml
	python -m build
	$(SED) "s/$(VERSION)/999999/" pyproject.toml

# .PHONY
# api:
#     openapi-python-client generate --url https://api.swaggerhub.com/apis/buildingSMART/BCF/3.0