all: README.html
	bash recoll-status.sh

README.html : README.rst
	rst2html README.rst > README.html
