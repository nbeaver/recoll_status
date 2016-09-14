all: readme.html todo.html
	python recoll_status.py

readme.html : readme.rst
	rst2html readme.rst.rst readme.html

todo.html : todo.md
	markdown todo.md > todo.html

clean :
	rm -f readme.html
