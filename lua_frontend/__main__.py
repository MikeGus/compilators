import argparse
import sys

import ply.lex as lex
import ply.yacc as yacc

import lua_lexer_rules
import lua_parser


def main():
    parser = argparse.ArgumentParser(description='Parse lua file into AST and display it to stdout')
    parser.add_argument('-s', '--source', type=str, help='source file')
    parser.add_argument('-d', '--destination', type=str, help='destination file for serialized AST')
    args = parser.parse_args()

    if args.source is not None:
        source = open(args.source)
        data = source.read()
    else:
        data = sys.stdin.read()

    lexer = lex.lex(module=lua_lexer_rules)
    parser = yacc.yacc(module=lua_parser)
    ast = parser.parse(data, lexer=lexer)

    if args.destination:
        destination = open(args.destination, 'w')
        print(ast, file=destination)
    else:
        print(ast)


if __name__ == '__main__':
    main()
