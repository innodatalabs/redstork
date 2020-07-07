.PHONY: docs docker test so

all: wheel

export PATH := $(PATH):/depot_tools
ON_TAG := $(shell git tag --points-at HEAD)

so: src/*.cc
	ninja -C /out/Debug
	ninja -C /out/Release
	cp /out/Release/lib*.so redstork/linux/

sodbg: so
	cp /out/Debug/lib*.so redstork/linux/

test:
	pip install pytest
	pytest

wheel: test
	rm -rf build dist
	pip install wheel
	python setup.py bdist_wheel

publish: wheel
	pip install twine
	twine upload dist/*.whl -u __token__ -p $(PYPI_TOKEN)

maybe_publish:
ifneq ($(ON_TAG),)
	pip install twine
	twine upload dist/redstork*.whl -u __token__ -p $(PYPI_TOKEN)
endif

docs:
	(cd docs; make html)

docker:
	docker build -t mkroutikov/redstork -f docker/Dockerfile .
