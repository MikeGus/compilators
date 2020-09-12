reserved = {
    'and': 'AND',
    'break': 'BREAK',
    'do': 'DO',
    'else': 'ELSE',
    'elseif': 'ELSEIF',
    'end': 'END',
    'false': 'FALSE',
    'for': 'FOR',
    'function': 'FUNCTION',
    'goto': 'GOTO',
    'if': 'IF',
    'in': 'IN',
    'local': 'LOCAL',
    'nil': 'NIL',
    'not': 'NOT',
    'or': 'OR',
    'repeat': 'REPEAT',
    'return': 'RETURN',
    'then': 'THEN',
    'true': 'TRUE',
    'until': 'UNTIL',
    'while': 'WHILE',
}

tokens = [
    'NAME',
    'NUMBER',
    'LITERAL_STRING',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'MOD',
    'POW',
    'LENGTH',
    'BITWISE_AND',
    'BITWISE_NOT',
    'BITWISE_OR',
    'LSHIFT',
    'RSHIFT',
    'INT_DIVIDE',
    'EQUALS',
    'NOT_EQUALS',
    'LESS_OR_EQUAL',
    'GREATER_OR_EQUAL',
    'LESS_THAN',
    'GREATER_THAN',
    'ASSIGNMENT',
    'ROUND_LBRACKET',
    'ROUND_RBRACKET',
    'LBRACE',
    'RBRACE',
    'SQUARE_LBRACKET',
    'SQUARE_RBRACKET',
    'DOUBLE_COLON',
    'SEMICOLON',
    'COLON',
    'COMMA',
    'VARARG',
    'CONCAT',
    'DOT'
] + list(reserved.values())


def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'NAME')
    if t.type == 'NIL':
        t.value = None
    elif t.type == 'TRUE':
        t.value = True
    elif t.type == 'FALSE':
        t.value = False
    return t


def t_NUMBER(t):
    r'((\d*\.\d+)|(\d+\.\d*)|(\d+))'
    t.value = float(t.value)
    return t


def t_LITERAL_STRING(t):
    r'(\'.*\')|(\".*\")'
    return t


t_ignore_COMMENT = r'\-\-.*'
t_PLUS = r'\+'
t_MINUS = r'\-'
t_TIMES = r'\*'
t_DIVIDE = r'\/'
t_MOD = r'\%'
t_POW = r'\^'
t_LENGTH = r'\#'
t_BITWISE_AND = r'\&'
t_BITWISE_NOT = r'\~'
t_BITWISE_OR = r'\|'
t_LSHIFT = r'\<\<'
t_RSHIFT = r'\>\>'
t_INT_DIVIDE = r'\/\/'
t_EQUALS = r'\=\='
t_NOT_EQUALS = r'\~\='
t_LESS_OR_EQUAL = r'\<\='
t_GREATER_OR_EQUAL = r'\>\='
t_LESS_THAN = r'\<'
t_GREATER_THAN = r'\>'
t_ASSIGNMENT = r'\='
t_ROUND_LBRACKET = r'\('
t_ROUND_RBRACKET = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SQUARE_LBRACKET = r'\['
t_SQUARE_RBRACKET = r'\]'
t_DOUBLE_COLON = r'\:\:'
t_SEMICOLON = r'\;'
t_COLON = r'\:'
t_COMMA = r'\,'
t_VARARG = r'\.\.\.'
t_CONCAT = r'\.\.'
t_DOT = r'\.'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


t_ignore = ' \t'


def t_error(t):
    print("Illegal character '{}'".format(t.value[0]))
    t.lexer.skip(1)
