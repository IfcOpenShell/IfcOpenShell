VERSION:=`date '+%y%m%d'`
SED:=sed -i
ifeq ($(UNAME_S),Darwin)
SED:=sed -i '' -e
endif

.PHONY: test
test:
	pytest -p no:pytest-blender test

.PHONY: dist
dist:
	rm -rf dist
	$(SED) "s/999999/$(VERSION)/" pyproject.toml
	python -m build
	$(SED) "s/$(VERSION)/999999/" pyproject.toml
