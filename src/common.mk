include ../vars.mk

.PHONY: dist
dist:
	rm -rf build
	mkdir -p build
	mkdir -p dist
	cp -r $(PACKAGE_NAME) build/
ifdef EXTRA_MODULES
	cp -r $(EXTRA_MODULES) build/
endif
	cp pyproject.toml build/
	if [ -f README.md ]; then cp README.md build/; fi
ifeq ($(IS_STABLE), TRUE)
	$(SED) 's/version = "0.0.0"/version = "$(VERSION_PYTHON)"/' build/pyproject.toml
ifdef IS_MODULE
	$(SED) 's/version = "0.0.0"/version = "$(VERSION_PYTHON)"/' build/$(PACKAGE_NAME)
else
	$(SED) 's/version = "0.0.0"/version = "$(VERSION_PYTHON)"/' build/$(PACKAGE_NAME)/__init__.py
endif
else
	$(SED) 's/version = "0.0.0"/version = "$(VERSION_DAILY)"/' build/pyproject.toml
ifdef IS_MODULE
	$(SED) 's/version = "0.0.0"/version = "$(VERSION_DAILY)"/' build/$(PACKAGE_NAME)
else
	$(SED) 's/version = "0.0.0"/version = "$(VERSION_DAILY)"/' build/$(PACKAGE_NAME)/__init__.py
endif
endif
	# Prefer uv when available - it's faster, as it skips creating a venv and installing build.
	cd build && if command -v uv >/dev/null 2>&1; then \
		uv build --wheel; \
	else \
		$(PYTHON) -m venv env && . env/$(VENV_ACTIVATE) && $(PIP) install build && \
		$(PYTHON) -m build --wheel; \
	fi
	cp build/dist/*.whl dist/
	rm -rf build
