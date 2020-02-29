.PHONY: all test clean

all: readme.html todo.html
	./recollstatus.py

readme.html : readme.rst
	rst2html readme.rst readme.html

todo.html : todo.md
	markdown todo.md > todo.html

test :
	./test_recollstatus.py

.PHONY: format
format :
	yapf3 --in-place recollstatus.py

clean :
	rm -f readme.html
