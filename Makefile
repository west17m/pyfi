HOST=127.0.0.1
TEST_PATH=./tests

clean:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive .cache/
	rm --force MANIFEST

init:
	pip install -r requirements.txt

test:
	python -m pytest --verbose --color=yes $(TEST_PATH)

install:
	python setup.py install

dist:
	python setup.py sdist

run:
	python pyfi/pyfi_cli.py

help:
	@echo "    clean"
	@echo "        Remove python and build artifacts."
	@echo "    init"
	@echo "        Install the requirements."
	@echo "    test"
	@echo "        Run tests."
	@echo "    install"
	@echo "        Install PyFi"
	@echo '    dist'
	@echo '        Prepare package for distribution.'
	@echo '    run'
	@echo '        Run PyFi from the command line.'
	@echo '    help'
	@echo '        Display this message.'
