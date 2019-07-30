# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# Remove tox testing artifacts
.PHONY: clean-tox
clean-tox:
	@echo "+ $@"
	@rm -rf .tox/

# Remove build artifacts
.PHONY: clean-build
clean-build:
	@echo "+ $@"
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info

# Remove python file artifacts
.PHONY: clean-pyc
clean-pyc:
	@echo "+ $@"
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type f -name '*.py[co]' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +

# Remove all artifacts
.PHONY: clean
clean: clean-tox clean-build clean-pyc

# Run linter
.PHONY: lint
lint:
	@echo "+ $@"
	@tox -e flake8

 # Run tests
.PHONY: test
test:
	@echo "+ $@"
	@tox -e py3

# Build
.PHONY: build
build:
	python3 setup.py build

# Tag
VERSION ?= $(shell python3 -c 'import tracker; print(tracker.__version__)')

.PHONY: tag
tag:
	@echo "+ $@ $(VERSION)"
	@git tag -a -f $(VERSION) -m 'Version $(VERSION)'
	@git push --tags

# Package and upload release to PyPi
.PHONY: release
release: clean
	@echo "+ $@"
	@python3 setup.py sdist bdist_wheel
	#@twine upload -r $(PYPI_SERVER) dist/*

# Build bdist_wheel distribution
.PHONY: wheel
wheel: clean
	@echo "+ $@"
	@python3 setup.py bdist_wheel
	@ls -l dist

# Install package
.PHONY: install
install: clean
	@echo "+ $@"
	@pip3 install -e .

# Validating local version prior to committing.
.PHONY: commit-check
commit-check:
	make lint
	make test
	@echo "Commit check passed on `python --version 2>&1`"
