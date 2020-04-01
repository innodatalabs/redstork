.PHONY: docs docker

all: wheel

export PATH := $(PATH):/depot_tools

so: src/*.cc
	ninja -C /out/Debug
	ninja -C /out/Release

wheel: so
	cp /out/Release/lib*.so redstork/linux/
	rm -rf build dist
	python setup.py bdist_wheel

publish: wheel
	pip install twine
	twine upload dist/*.whl -u $(USER) -p $(PASS)

docs:
	(cd docs; make html)

docker:
	docker build -t redstork:dev -f docker/Dockerfile .
