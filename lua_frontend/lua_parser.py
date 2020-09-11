import json

import ply.lex as lex
import ply.yacc as yacc

import lua_lexer_rules
from lua_lexer_rules import tokens


def dumps(d):
    return json.dumps(d, indent=4, separators=(',', ': '))


class Chunk:
    def __init__(self, block=None):
        self.block = block

    def __str__(self):
        return dumps({'block': str(self.block)})


def p_chunk_block(p):
    'chunk: block'
    p[0] = Chunk(p[1])


class Block:
    def __init__(self, statement_list=None, retstatement=None):
        self.statement_list = statement_list
        self.retstatement = retstatement

    def __str__(self):
        return dumps({
            'statement_list': str(self.statement_list),
            'retstatement': str(self.retstatement)
        })


def p_block_statement(p):
    'block: statement_list [retstatement]'
    p[0] = Block(statement_list=p[1], retstatement=p[2])


class StatementList:
    def __init__(self, statement=None, statement_list=None):
        self.statements = []
        if statement is not None:
            self.statements.append(statement)
        if statement_list.statements is not []:
            self.statements.extend(statement_list.statements)

    def __str__(self):
        return dumps({'statements': [str(st) for st in self.statements]})


def p_statement_list(p):
    '''statement_list: statement statement_list
                     | empty '''
    if len(p) == 3:
        p[0] = StatementList(p[1], p[2])
    else:
        p[0] = StatementList()


class VariableList:
    def __init__(self, variable=None, variable_list=None):
        self.variables = []
        if variable is not None:
            self.variables.append(variable)
        if variable_list.variables is not []:
            self.variables.extend(variable_list.variables)

    def __str__(self):
        return dumps({'variables': [str(var) for var in self.variables]})


def p_variable_list(p):
    '''variable_list: variable COMMA variable_list
                    | variable'''
    if len(p) == 4:
        p[0] = VariableList(p[1], p[2])
    elif p[1]:
        p[0] = VariableList(p[1])
    else:
        p[0] = VariableList()


class ExpressionList:
    def __init__(self, expression=None, expression_list=None):
        self.expressions = []
        if expression is not None:
            self.expressions.append(expression)
        if expression_list.expressions is not []:
            self.expressions.extend(expression_list.expressions)

    def __str__(self):
        return dumps({'expressions': [str(exp) for exp in self.expressions]})


def p_expression_list(p):
    '''expression_list: expression COMMA expression_list
                      | expression'''
    if len(p) == 4:
        p[0] = ExpressionList(p[1], p[2])
    elif p[1]:
        p[0] = ExpressionList(p[1])
    else:
        p[0] = ExpressionList()


class NameList:
    def __init__(self, name=None, name_list=None):
        self.names = []
        if name is not None:
            self.names.append(name)
        if name_list.names is not []:
            self.names.extend(name_list.names)

    def __str__(self):
        return dumps({'names': [str(name) for name in self.names]})


def p_name_list(p):
    '''name_list: NAME COMMA name_list
                | NAME'''
    if len(p) == 4:
        p[0] = NameList(p[1], p[2])
    elif p[1]:
        p[0] = NameList(p[1])
    else:
        p[0] = NameList()


def p_empty(p):
    'empty:'
    pass


class Assignment:
    def __init__(self, variable_list=None, expression_list=None):
        self.variable_list = variable_list
        self.expression_list = expression_list

    def __str__(self):
        return dumps({'variable_list': str(self.variable_list), 'expression_list': str(self.expression_list)})


def p_assignment(p):
    'assignment: varlist EQUALS explist'
    p[0] = Assignment(p[1], p[3])


class DoBlock:
    def __init__(self, block=None):
        self. block = block

    def __str__(self):
        return dumps({'block': str(self.block)})


def p_do_block(p):
    'do_block: DO block END'
    p[0] = DoBlock(p[2])


class WhileLoop:
    def __init__(self, expression=None, block=None):
        self.expression = expression
        self.block = block

    def __str__(self):
        return dumps({'expression': str(self.expression), 'block': str(self.block)})


def p_while_loop(p):
    'while_loop: WHILE expression DO block END'
    p[0] = WhileLoop(p[2], p[4])


class RepeatLoop:
    def __init__(self, block=None, expression=None):
        self.block = block
        self.expression = expression

    def __str__(self):
        return dumps({'expression': str(self.expression), 'block': str(self.block)})


def p_repeat_loop(p):
    'repeat_loop: REPEAT block UNTIL expression'
    p[0] = RepeatLoop(p[2], p[4])


class GoTo:
    def __init__(self, label=None):
        self.label = label

    def __str__(self):
        return dumps({'label': str(self.label)})


def p_goto(p):
    'goto: GOTO NAME'
    p[0] = GoTo(p[2])


class IfItem:
    def __init__(self, condition=None, block=None):
        self.condition = condition
        self.block = block

    def __str__(self):
        return dumps({'condition': self.condition,  'block': self.block})


def p_elseif_item(p):
    'elseif_item: ELSEIF expression THEN block'
    p[0] = IfItem(p[2], p[4])


class ElseIfList:
    def __init__(self, elseif_item=None, elseif_list=None):
        self.sequence = []
        if elseif_item is not None:
            self.sequence.append(elseif_item)
        if elseif_list is not None:
            self.sequence.extend(elseif_list.sequence)


class If:
    def __init__(self, expression=None, block=None, elseif_list=None, lastblock=None):
        self.sequence = []
        if expression is not None and block is not None:
            self.sequence.apppend(IfItem(expression, block))
        if elseif_list is not None:
            self.sequence.extend(elseif_list.sequence)
        if lastblock is not None:
            self.sequence.append(IfItem(None, lastblock))

    def __str__(self):
        return dumps({'sequence': [str(el) for el in self.sequence]})


def p_if(p):
    '''if: IF expression THEN block elseif_list ELSE block END
         | IF expression THEN block elseif_list END'''
    if len(p) == 9:
        p[0] = If(p[2], p[4], p[5], p[7])
    else:
        p[0] = If(p[2], p[4], p[5])


class ForStart:
    def __init__(self, name=None, expression=None):
        self.name = name
        self.expression = expression

    def __str__(self):
        return dumps({'name': self.name, 'expression': self.expression})


class ForLoop:
    def __init__(self, name=None, expression=None, end_condition=None, repeated_expression=None, block=None):
        self.start_assignment = ForStart(name, expression)
        self.end_condition = end_condition
        if repeated_expression is not None:
            self.repeated_expression = repeated_expression
        self.block = block

    def __str__(self):
        d = {
            'start_assignment': str(self.start_assignment),
            'end_condition': str(self.end_condition),
            'block': str(self.block),
        }
        if self.repeated_expression:
            d['repeated_expression'] = str(self.repeated_expression)
        return dumps(d)


def p_for_loop(p):
    '''for_loop: FOR NAME EQUALS expression COMMA expression COMMA expression DO block END
               | FOR NAME EQUALS expression COMMA expression DO block END
    '''
    if len(p) == 11:
        p[0] = ForLoop(p[2], p[4], p[6], p[8], p[10])
    else:
        p[0] = ForLoop(p[2], p[4], p[6], None, p[8])


class RangeBasedFor:
    def __init__(self, names=None, expressions=None, block=None):
        self.names = names
        self.expressions = expressions
        self.block = block

    def __str__(self):
        return dumps({'names': [str(name) for name in self.names], 'expressions': [str(exp) for exp in self.expressions], 'block': str(self.block)})


def p_range_based_for(p):
    'ranged_based_for: FOR name_list IN expression_list DO block END'
    p[0] = RangeBasedFor(p[2], p[4], p[6])


class Function:
    def __init__(self, name=None, body=None):
        self.name = name
        self.body = body

    def __str__(self):
        return dumps({'name': str(self.name), 'body': self(self.body)})


def p_function(p):
    'function: FUNCTION funcname funcbody'
    p[0] = Function(p[2], p[3])


class LocalFunction:
    def __init__(self, name=None, body=None):
        self.name = name
        self.body = body

    def __str__(self):
        return dumps({'name': self.name, 'body': self.body})


def p_local_function(p):
    'local_function: LOCAL FUNCTION NAME funcbody'
    p[0] = LocalFunction(p[3], p[4])


class Attribute:
    def __init__(self, attribute=None):
        self.attribute = attribute

    def __str__(self):
        return dumps({'attribute': self.attribute})


def p_attribute(p):
    '''attribute: LESS_THAN NAME GREATER_THAN
                | empty'''
    if len(p) == 4:
        p[0] = Attribute(p[2])
    else:
        p[0] = Attribute()


class AttributeName:
    def __init__(self, name=None, attribute=None):
        self.name = name
        self.attribute = attribute

    def __str__(self):
        return dumps({'name': str(self.name), 'attribute': str(self.attribute)})


def p_attribute_name(p):
    'attribute_name: NAME attribute'
    p[0] = AttributeName(p[1], p[2])


class AttributeNameList:
    def __init__(self, attribute=None, attribute_list=None):
        self.attributes = [attribute]
        if attribute_list is not None:
            self.attributes.extend(attribute_list.attributes)

    def __str__(self):
        return dumps({'attributes': [str(attr) for attr in self.attributes]})


def p_attribute_name_list(p):
    '''attribute_name_list: NAME attribute COMMA attribute_name_list
                          | NAME attribute'''
    if len(p) == 5:
        p[0] = AttributeNameList(p[2], p[4])
    else:
        p[0] = AttributeNameList(p[2])


class LocalAttributeListAssignment:
    def __init__(self, attributes=None, expressions=None):
        self.attributes = attributes
        self.expressions = expressions

    def __str__(self):
        return dumps({'attributes': str(self.attributes), 'expressions': str(self.expressions)})


def p_local_attribute_list_assignment(p):
    '''local_attribute_list_assignment: LOCAL attribute_name_list EQUALS expression_list
                                      | LOCAL attribute_name_list'''
    if len(p) == 5:
        p[0] = LocalAttributeListAssignment(p[2], p[4])
    else:
        p[0] = LocalAttributeListAssignment(p[2])


class Statement:
    def __init__(self, statement=None):
        self.statement = statement

    def __str__(self):
        return dumps({'statement': str(self.statement)})


def p_statement(p):
    '''statement : SEMICOLON
                 | assignment
                 | functioncall
                 | label
                 | BREAK
                 | goto
                 | do_block
                 | while_loop
                 | repeat_loop
                 | if
                 | for_loop
                 | ranged_based_for
                 | function
                 | local_function
                 | local_attribute_list_assignment'''
    p[0] = Statement(p[1])


class ReturnStatement:
    def __init__(self, expressions=None):
        self.expressions = expressions

    def __str__(self):
        return dumps({'expressions': str(self.expressions)})


def p_return_statement(p):
    '''return_statement: RETURN expression_list SEMICOLON
                       | RETURN expression_list
                       | RETURN SEMICOLON
                       | RETURN'''
    if len(p) > 2 and isinstance(p[2], ExpressionList):
        p[0] = ReturnStatement(p[2])
    else:
        p[0] = ReturnStatement()


class Label:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return dumps({'name': self.name})


def p_label(p):
    'label: DOUBLE_COLON NAME DOUBLE_COLON'
    p[0] = Label(p[3])


class NameChain:
    def __init__(self, name=None, chain=None):
        self.names = [name]
        if chain is not None:
            self.names.extend(chain.names)


def p_name_chain(p):
    '''name_chain: NAME DOT name_chain
                 | NAME'''
    if len(p) == 4:
        p[0] = NameChain(p[1], p[3])
    else:
        p[0] = NameChain(p[1])


class FuncName:
    def __init__(self, object_name=None, function_name=None):
        self.object_name = object_name
        self.function_name = function_name

    def __str__(self):
        d = {'function_name': self.function_name}
        if self.object_name is not None:
            d['object_name'] = self.object_name
        return dumps(d)


def p_funcname(p):
    '''funcname: name_chain COLON name
               | name_chain'''
    if len(p) == 4:
        p[0] = FuncName(object_name=p[1], function_name=p[3])
    else:
        p[0] = FuncName(function_name=p[1])


class ObjectField:
    def __init__(self, obj=None, field=None):
        self.obj = obj
        self.field = field

    def __str__(self):
        return dumps({'object': str(self.obj), 'field': str(self.field)})


def p_object_field(p):
    '''object_field: prefixexp SQUARE_LBRACKET expression SQUARE_RBRACKET
                   | prefixexp DOT NAME'''
    if len(p) == 5:
        p[0] = ObjectField(p[1], p[3])
    else:
        p[0] = ObjectField(p[1], p[3])


class Variable:
    def __init__(self, identifier=None):
        self.identifier = identifier

    def __str__(self):
        return dumps({'identifier': self.identifier})


def p_variable(p):
    '''variable: NAME
               | object_field'''
    p[0] = Variable(p[1])


class PrefixExpression:
    def __init__(self, expression=None):
        self.expression = expression

    def __str__(self):
        return dumps({'expression': self.expression})


def p_prefixexp(p):
    '''prefixexp: variable
                | functioncall
                | ROUND_LBRACKET expression RBRACKET'''
    if len(p) == 4:
        p[0] = PrefixExpression(p[2])
    else:
        p[0] = PrefixExpression(p[1])


class FunctionCall:
    def __init__(self, prefix=None, name=None, args=None):
        self.prefix = prefix
        self.name = name
        self.args = args

    def __str__(self):
        d = {
            'prefix': str(self.prefix),
            'args': str(self.args),
        }
        if self.name is not None:
            d['name'] = self.name
        return dumps(d)


def p_functioncall(p):
    '''functioncall: prefixexp args
                   | prefixexp COLON NAME args'''
    if len(p) == 5:
        p[0] = FunctionCall(p[1], p[3], p[4])
    else:
        p[0] = FunctionCall(p[1], None, p[2])


class Args:
    def __init__(self, args=[]):
        self.args = args

    def __str__(self):
        return dumps({'args': self.args})


def p_args(p):
    '''args: ROUND_LBRACKET expression_list ROUND_RBRACKET
           | ROUND_LBRACKET ROUND_RBRACKET
           | table_constructor
           | LITERAL_STRING'''
    if len(p) == 4:
        p[0] = Args(p[2])
    elif len(p) == 2:
        p[0] = Args(p[2])
    else:
        p[0] = Args()


class FunctionDef:
    def __init__(self, body=None):
        self.body = body

    def __str__(self):
        return dumps({'body': self.body})


def p_function_def(p):
    'functiondef: FUNCTION funcbody'
    p[0] = FunctionDef(p[2])


class FuncBody:
    def __init__(self, parlist=None, block=None):
        pass


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
    parser = yacc.yacc()
    parser.parse(data, lexer=lexer)


if __name__ == '__main__':
    main()
