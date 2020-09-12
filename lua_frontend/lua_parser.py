import json

from lua_lexer_rules import tokens  # noqa: W0611


start = 'chunk'


def p_error(p):
    if p:
        print("Syntax error at token", p.type)
    else:
        print("Syntax error at EOF")


def p_empty(p):
    'empty : '
    pass


def p_fieldsep(p):
    '''fieldsep : COMMA
                | SEMICOLON'''
    pass


class ASTNode:
    def __str__(self):
        d = {
            'node_type': self.__class__.__name__
        }
        for k, v in vars(self).items():
            if v is None:
                continue
            if isinstance(v, list):
                d[k] = []
                for el in v:
                    if issubclass(el.__class__, ASTNode):
                        el = json.loads(str(el))
                    d[k].append(el)
            elif issubclass(v.__class__, ASTNode):
                d[k] = json.loads(str(v))
            else:
                d[k] = v
        return json.dumps(d, indent=4, separators=(',', ': '), sort_keys=True)


class Chunk(ASTNode):
    def __init__(self, block):
        self.block = block


def p_chunk_block(p):
    'chunk : block'
    p[0] = Chunk(p[1])


class Block(ASTNode):
    def __init__(self, statement_list, return_statement=None):
        self.statement_list = statement_list
        self.return_statement = return_statement


def p_block_statement(p):
    '''block : statement_list return_statement
             | statement_list'''
    if len(p) == 3:
        p[0] = Block(p[1], p[2])
    else:
        p[0] = Block(p[1])


class StatementList(ASTNode):
    def __init__(self, statement=None, statement_list=None):
        self.statements = []
        if statement is not None:
            self.statements.append(statement)
        if statement_list is not None:
            self.statements.extend(statement_list.statements)


def p_statement_list(p):
    '''statement_list : statement statement_list
                      | empty'''
    if len(p) == 3:
        p[0] = StatementList(p[1], p[2])
    else:
        p[0] = StatementList()


class VariableList(ASTNode):
    def __init__(self, variable, variable_list=None):
        self.variables = [variable]
        if variable_list is not None:
            self.variables.extend(variable_list.variables)


def p_variable_list(p):
    '''variable_list : variable COMMA variable_list
                     | variable'''
    if len(p) == 4:
        p[0] = VariableList(p[1], p[2])
    else:
        p[0] = VariableList(p[1])


class ExpressionList(ASTNode):
    def __init__(self, expression, expression_list=None):
        self.expressions = [expression]
        if expression_list is not None:
            self.expressions.extend(expression_list.expressions)


def p_expression_list(p):
    '''expression_list : expression COMMA expression_list
                       | expression'''
    if len(p) == 4:
        p[0] = ExpressionList(p[1], p[2])
    else:
        p[0] = ExpressionList(p[1])


class NameList(ASTNode):
    def __init__(self, name, name_list=None):
        self.names = [name]
        if name_list is not None:
            self.names.extend(name_list.names)


def p_name_list(p):
    '''name_list : name COMMA name_list
                 | name'''
    if len(p) == 4:
        p[0] = NameList(p[1], p[2])
    else:
        p[0] = NameList(p[1])


class Assignment(ASTNode):
    def __init__(self, variable_list, expression_list):
        self.variable_list = variable_list
        self.expression_list = expression_list


def p_assignment(p):
    'assignment : variable_list ASSIGNMENT expression_list'
    p[0] = Assignment(p[1], p[3])


class DoBlock(ASTNode):
    def __init__(self, block):
        self. block = block


def p_do_block(p):
    'do_block : DO block END'
    p[0] = DoBlock(p[2])


class WhileLoop(ASTNode):
    def __init__(self, expression, block):
        self.expression = expression
        self.block = block


def p_while_loop(p):
    'while_loop : WHILE expression DO block END'
    p[0] = WhileLoop(p[2], p[4])


class RepeatLoop(ASTNode):
    def __init__(self, block, expression):
        self.block = block
        self.expression = expression


def p_repeat_loop(p):
    'repeat_loop : REPEAT block UNTIL expression'
    p[0] = RepeatLoop(p[2], p[4])


class GoTo(ASTNode):
    def __init__(self, label):
        self.label = label


def p_goto(p):
    'goto : GOTO name'
    p[0] = GoTo(p[2])


class IfItem(ASTNode):
    def __init__(self, block, condition=None):
        self.block = block
        self.condition = condition


def p_elseif_item(p):
    'elseif_item : ELSEIF expression THEN block'
    p[0] = IfItem(p[4], p[2])


class ElseIfList:
    def __init__(self, elseif_item=None, elseif_list=None):
        self.sequence = []
        if elseif_item is not None:
            self.sequence.append(elseif_item)
        if elseif_list is not None:
            self.sequence.extend(elseif_list.sequence)


def p_elsif_list(p):
    '''elseif_list : elseif_item elseif_list
                   | empty'''
    if len(p) == 3:
        p[0] = ElseIfList(p[1], p[2])
    else:
        p[0] = ElseIfList()


class If(ASTNode):
    def __init__(self, expression, block, elseif_list=None, lastblock=None):
        self.sequence = []
        self.sequence.append(IfItem(block, expression))
        if elseif_list is not None:
            self.sequence.extend(elseif_list.sequence)
        if lastblock is not None:
            self.sequence.append(IfItem(None, lastblock))


def p_if(p):
    '''if : IF expression THEN block elseif_list ELSE block END
          | IF expression THEN block elseif_list END'''
    if len(p) == 9:
        p[0] = If(p[2], p[4], p[5], p[7])
    else:
        p[0] = If(p[2], p[4], p[5])


class ForStart(ASTNode):
    def __init__(self, name=None, expression=None):
        self.name = name
        self.expression = expression


class ForLoop(ASTNode):
    def __init__(self, name, expression, end_condition, block, repeated_expression=None):
        self.start_assignment = ForStart(name, expression)
        self.end_condition = end_condition
        self.block = block
        self.repeated_expression = repeated_expression


def p_for_loop(p):
    '''for_loop : FOR name ASSIGNMENT expression COMMA expression COMMA expression DO block END
                | FOR name ASSIGNMENT expression COMMA expression DO block END
    '''
    if len(p) == 11:
        p[0] = ForLoop(p[2], p[4], p[6], p[10], p[8])
    else:
        p[0] = ForLoop(p[2], p[4], p[6], p[8])


class RangeBasedFor(ASTNode):
    def __init__(self, names, expressions, block):
        self.names = names
        self.expressions = expressions
        self.block = block


def p_range_based_for(p):
    'ranged_based_for : FOR name_list IN expression_list DO block END'
    p[0] = RangeBasedFor(p[2], p[4], p[6])


class Function(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body


def p_function(p):
    'function : FUNCTION funcname funcbody'
    p[0] = Function(p[2], p[3])


class LocalFunction(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body


def p_local_function(p):
    'local_function : LOCAL FUNCTION name funcbody'
    p[0] = LocalFunction(p[3], p[4])


class Attribute(ASTNode):
    def __init__(self, name=None):
        self.name = name


def p_attribute(p):
    '''attribute : LESS_THAN name GREATER_THAN
                 | empty'''
    if len(p) == 4:
        p[0] = Attribute(p[2])
    else:
        p[0] = Attribute()


class ObjectAttribute(ASTNode):
    def __init__(self, object_name=None, attribute=None):
        self.object_name = object_name
        self.attribute = attribute


def p_object_attribute(p):
    'object_attribute : name attribute'
    p[0] = ObjectAttribute(p[1], p[2])


class ObjectAttributeList(ASTNode):
    def __init__(self, attribute, attribute_list=None):
        self.object_attributes = [attribute]
        if attribute_list is not None:
            self.attributes.extend(attribute_list.object_attributes)


def p_object_attribute_list(p):
    '''object_attribute_list : object_attribute COMMA object_attribute_list
                             | object_attribute'''
    if len(p) == 5:
        p[0] = ObjectAttributeList(p[2], p[4])
    else:
        p[0] = ObjectAttributeList(p[2])


class LocalObjectAttributeListAssignment(ASTNode):
    def __init__(self, object_attributes, expressions=None):
        self.object_attributes = object_attributes
        self.expressions = expressions


def p_local_object_attribute_list_assignment(p):
    '''local_object_attribute_list_assignment : LOCAL object_attribute_list ASSIGNMENT expression_list
                                             | LOCAL object_attribute_list'''
    if len(p) == 5:
        p[0] = LocalObjectAttributeListAssignment(p[2], p[4])
    else:
        p[0] = LocalObjectAttributeListAssignment(p[2])


class Statement(ASTNode):
    def __init__(self, statement):
        self.statement = statement


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
                 | local_object_attribute_list_assignment'''
    p[0] = Statement(p[1])


class ReturnStatement(ASTNode):
    def __init__(self, expressions=None):
        self.expressions = expressions


def p_return_statement(p):
    '''return_statement : RETURN expression_list SEMICOLON
                        | RETURN expression_list
                        | RETURN SEMICOLON
                        | RETURN'''
    if len(p) > 2 and isinstance(p[2], ExpressionList):
        p[0] = ReturnStatement(p[2])
    else:
        p[0] = ReturnStatement()


class Label(ASTNode):
    def __init__(self, name):
        self.name = name


def p_label(p):
    'label : DOUBLE_COLON name DOUBLE_COLON'
    p[0] = Label(p[3])


class NameChain(ASTNode):
    def __init__(self, name, chain=None):
        self.names = [name]
        if chain is not None:
            self.names.extend(chain.names)


def p_name_chain(p):
    '''name_chain : name DOT name_chain
                  | name'''
    if len(p) == 4:
        p[0] = NameChain(p[1], p[3])
    else:
        p[0] = NameChain(p[1])


class FuncName(ASTNode):
    def __init__(self, name_chain, name=None):
        self.name_chain = name_chain.names
        if name is not None:
            self.name_chain.append(name)


def p_funcname(p):
    '''funcname : name_chain COLON name
                | name_chain'''
    if len(p) == 4:
        p[0] = FuncName(p[1], p[3])
    else:
        p[0] = FuncName(p[1])


class ObjectField(ASTNode):
    def __init__(self, object_name, field):
        self.object_name = object_name
        self.field = field


def p_object_field(p):
    '''object_field : prefixexp SQUARE_LBRACKET expression SQUARE_RBRACKET
                    | prefixexp DOT name'''
    if len(p) == 5:
        p[0] = ObjectField(p[1], p[3])
    else:
        p[0] = ObjectField(p[1], p[3])


class Variable(ASTNode):
    def __init__(self, identifier):
        self.identifier = identifier


def p_variable(p):
    '''variable : name
                | object_field'''
    p[0] = Variable(p[1])


class PrefixExpression(ASTNode):
    def __init__(self, expression):
        self.expression = expression


def p_prefixexp(p):
    '''prefixexp : variable
                 | functioncall
                 | ROUND_LBRACKET expression ROUND_RBRACKET'''
    if len(p) == 4:
        p[0] = PrefixExpression(p[2])
    else:
        p[0] = PrefixExpression(p[1])


class FunctionCall(ASTNode):
    def __init__(self, prefix, args, name=None):
        self.prefix = prefix
        self.args = args
        self.name = name


def p_functioncall(p):
    '''functioncall : prefixexp args
                    | prefixexp COLON name args'''
    if len(p) == 5:
        p[0] = FunctionCall(p[1], p[4], p[3])
    else:
        p[0] = FunctionCall(p[1], p[2])


class Args(ASTNode):
    def __init__(self, args=[]):
        self.args = args


def p_args(p):
    '''args : ROUND_LBRACKET expression_list ROUND_RBRACKET
            | ROUND_LBRACKET ROUND_RBRACKET
            | table_constructor
            | literal_string'''
    if len(p) == 4:
        p[0] = Args(p[2])
    elif len(p) == 2:
        p[0] = Args(p[2])
    else:
        p[0] = Args()


class FunctionDef(ASTNode):
    def __init__(self, body):
        self.body = body


def p_function_def(p):
    'functiondef : FUNCTION funcbody'
    p[0] = FunctionDef(p[2])


class FuncBody(ASTNode):
    def __init__(self, block, parlist=None):
        self.block = block
        self.parlist = parlist


def p_funcbody(p):
    '''funcbody : ROUND_LBRACKET parlist ROUND_RBRACKET block END
                | ROUND_LBRACKET ROUND_RBRACKET block END'''
    if len(p) == 6:
        p[0] = FuncBody(p[4], p[2])
    else:
        p[0] = FuncBody(p[3])


class ParList(ASTNode):
    def __init__(self, namelist=None, vararg=False):
        self.namelist = namelist
        self.vararg = vararg


def p_parlist(p):
    '''parlist : name_list COMMA VARARG
               | name_list
               | VARARG'''
    if len(p) == 4:
        p[0] = ParList(p[1], True)
    elif isinstance(p[1], NameList):
        p[0] = ParList(p[1])
    else:
        p[0] = ParList(vararg=True)


class TableConstructor(ASTNode):
    def __init__(self, fieldlist=None):
        self.fieldlist = fieldlist


def p_table_constructor(p):
    '''table_constructor : LBRACE fieldlist RBRACE
                        | LBRACE RBRACE'''
    if len(p) == 4:
        p[0] = TableConstructor(p[2])
    else:
        p[0] = TableConstructor()


def FieldList(ASTNode):
    def __init__(self, field, fieldlist=None):
        self.fields = [field]
        if fieldlist is not None:
            self.fields.extend(fieldlist.fields)


class InnerFieldlist:
    def __init__(self, field=None, fieldlist=None):
        self.fields = []
        if field is not None:
            self.fields.append(field)
        if fieldlist is not None:
            self.fields.extend(fieldlist.fields)


def p_inner_fieldlist(p):
    '''inner_fieldlist : fieldsep field inner_fieldlist
                       | empty'''
    if len(p) == 4:
        p[0] = InnerFieldlist(p[2], p[3])
    else:
        p[0] = InnerFieldlist()


def p_fieldlist(p):
    '''fieldlist : field inner_fieldlist fieldsep
                 | field inner_fieldlist'''
    p[0] = FieldList(p[1], p[2])


class Field(ASTNode):
    def __init__(self, value, identifier=None):
        self.value = value
        self.identifier = identifier


def p_field(p):
    '''field : SQUARE_LBRACKET expression SQUARE_RBRACKET ASSIGNMENT expression
             | name ASSIGNMENT expression
             | expression'''
    if len(p) == 6:
        p[0] = Field(p[5], p[2])
    elif len(p) == 4:
        p[0] = Field(p[3], p[1])
    else:
        p[0] = Field(p[1])


class Expression(ASTNode):
    def __init__(self, expression):
        self.expression = expression


def p_expression(p):
    '''expression : NIL
                  | FALSE
                  | TRUE
                  | number
                  | literal_string
                  | VARARG
                  | functiondef
                  | prefixexp
                  | table_constructor
                  | binop
                  | unop'''
    p[0] = Expression(p[1])


class BinaryOperation(ASTNode):
    def __init__(self, left, right, operation):
        self.left = left
        self.right = right
        self.operation = operation


def p_binary_operation(p):
    '''binop : expression PLUS expression
             | expression MINUS expression
             | expression TIMES expression
             | expression DIVIDE expression
             | expression INT_DIVIDE expression
             | expression POW expression
             | expression MOD expression
             | expression BITWISE_AND expression
             | expression BITWISE_NOT expression
             | expression BITWISE_OR expression
             | expression RSHIFT expression
             | expression LSHIFT expression
             | expression CONCAT expression
             | expression LESS_THAN expression
             | expression LESS_OR_EQUAL expression
             | expression GREATER_THAN expression
             | expression GREATER_OR_EQUAL expression
             | expression EQUALS expression
             | expression NOT_EQUALS expression
             | expression AND expression
             | expression OR expression'''
    p[0] = BinaryOperation(p[1], p[3], p[2])


class UnaryOperation(ASTNode):
    def __init__(self, expression, operation):
        self.expression = expression
        self.operation = operation


def p_unnary_operation(p):
    '''unop : MINUS expression %prec UMINUS
            | NOT expression %prec UNOT
            | LENGTH expression
            | BITWISE_NOT expression %prec UBITWISE_NOT'''
    p[0] = UnaryOperation(p[2], p[1])


class Name(ASTNode):
    def __init__(self, name):
        self.name = name


def p_name(p):
    'name : NAME'
    p[0] = Name(p[1])


class LiteralString(ASTNode):
    def __init__(self, content):
        self.content = content


def p_literal_string(p):
    'literal_string : LITERAL_STRING'
    p[0] = LiteralString(p[1])


class Number(ASTNode):
    def __init__(self, value):
        self.value = value


def p_number(p):
    'number : NUMBER'
    p[0] = Number(p[1])


precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'LESS_THAN', 'GREATER_THAN', 'LESS_OR_EQUAL', 'GREATER_OR_EQUAL', 'NOT_EQUALS', 'EQUALS'),
    ('left', 'BITWISE_OR'),
    ('left', 'BITWISE_NOT'),
    ('left', 'BITWISE_AND'),
    ('left', 'LSHIFT', 'RSHIFT'),
    ('right', 'CONCAT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'INT_DIVIDE', 'MOD'),
    ('right', 'UNOT', 'LENGTH', 'UMINUS', 'UBITWISE_NOT'),
    ('right', 'POW'),
)
