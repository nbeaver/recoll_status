all: readme.html
	python recoll_status.py

readme.html : readme.rst
	rst2html readme.rst.rst > readme.html
