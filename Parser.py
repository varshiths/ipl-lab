from ipl.Parser import Parser

import sys
import os

from contextlib import redirect_stdout

LDBG = True
YDBG = True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error: Incorrect number of arguments")
        print("Usage: main.py program")
        sys.exit()
    input_file = os.path.basename(sys.argv[1])

    parser = Parser(parser_debug=YDBG, lexer_debug=LDBG)

    with open('Parser_ast_%s.txt' % input_file, 'w') as f:
    	with redirect_stdout(f):

		    with open(sys.argv[1], 'r') as f:
		        parser.process(f.read())