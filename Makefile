.PHONY: docs docker test so

all: wheel

export PATH := $(PATH):/depot_tools

so: src/*.cc
	ninja -C /out/Debug
	ninja -C /out/Release
	cp /out/Release/lib*.so redstork/linux/
	chmod 777 redstork/linux/*.so

test:
	pip install pytest
	pytest

wheel: test
	rm -rf wheelhouse
	mkdir wheelhouse
	pip wheel -v --wheel-dir=wheelhouse .

publish: wheel
	pip install twine
	twine upload wheelhouse/*.whl -u __token__ -p $(PYPI_TOKEN)

maybe_publish: wheel
ifeq ($(MYTAG), "")
	pip install twine
	twine upload diwheelhousest/*.whl -u __token__ -p $(PYPI_TOKEN)
endif

docs:
	(cd docs; make html)

docker:
	docker build -t mkroutikov/redstork -f docker/Dockerfile .
