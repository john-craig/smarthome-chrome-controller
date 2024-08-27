PYTHON = python3

build:
	$(PYTHON) -m build

install: build
	$(PYTHON) -m pip install --user --break-system-packages --force-reinstall dist/chromectrl-*-py3-none-any.whl