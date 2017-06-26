all: readme.html todo.html
	python recollstatus.py

readme.html : readme.rst
	rst2html readme.rst readme.html

todo.html : todo.md
	markdown todo.md > todo.html

test :
	python test_recollstatus.py

clean :
	rm -f readme.html
