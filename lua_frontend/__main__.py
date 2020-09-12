import ply.lex as lex
import ply.yacc as yacc

import lua_lexer_rules
import lua_parser


def main():
    data = '''
        -- defines a factorial function

        function fact (n)
          if n == 0 then
            return 1
          else
            return n * fact(n-1)
          end
        end


        print("enter a number:")
        a = io.read("*number")        -- read a number
        print(fact(a))

        local function sayHello()
            print("hello world !")
        end

        sayHello()
        l = -2
        q = 3
        print(-l + q)
    '''

    lexer = lex.lex(module=lua_lexer_rules)
    parser = yacc.yacc(module=lua_parser)
    ast = parser.parse(data, lexer=lexer)
    print(ast)


if __name__ == '__main__':
    main()
