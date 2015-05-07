.PHONY: clean

clean:
	find . -name '*.pyc' -delete
	find . -name '*$py.class' -delete
	find . -name '.DS_Store' -delete