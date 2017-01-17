HOST=127.0.0.1
TEST_PATH=./

clean:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force MANIFEST

init:
	pip install -r requirements.txt

test:
	py.test --verbose --color=yes $(TEST_PATH)

install:
	python setup.py install

dist:
	python setup.py sdist

run:
	python pyfi/pyfi_cli.py
