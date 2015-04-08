.PHONY: clean

clean:
	-find . -name "*.pyc" -print0 | xargs -r -0 rm
	-find . -name "*$py.class" -print0 | xargs -r -0 rm
	-find . -name ".DS_Store" -print0 | xargs -r -0 rm
