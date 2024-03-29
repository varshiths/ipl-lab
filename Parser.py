from ipl.Parser import Parser

import sys
import os

from contextlib import redirect_stdout

LDBG = False
YDBG = True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error: Incorrect number of arguments")
        print("Usage: main.py program")
        sys.exit()
    input_file = sys.argv[1]

    parser = Parser(parser_debug=YDBG, lexer_debug=LDBG)

    with open(sys.argv[1], 'r') as f:
        ast, cfg, sym, assembly = parser.process(f.read())

    with open(sys.argv[1] + ".ast", 'w+') as f:
        f.write(ast)
    with open(sys.argv[1] + ".cfg", 'w+') as f:
        f.write(cfg)
    with open(sys.argv[1] + ".sym", 'w+') as f:
        f.write(sym)
    with open(sys.argv[1] + ".s", 'w+') as f:
        f.write(assembly)
