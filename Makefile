clean:

	rm parsetab.py
	rm parser.out
	rm -rf __pycache__/
	rm *.out

runtest:

	python3 main.py test