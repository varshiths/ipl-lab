clean:

	rm -f parsetab.py
	rm -f parser.out
	rm -f -r __pycache__/
	rm -f *.out

runtest:

	python3 main.py test