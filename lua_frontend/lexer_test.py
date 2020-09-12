import ply.lex as lex

import lua_lexer_rules


def test_case(lexer, data, expected_tokens):
    lexer.input(data)
    for expected_token in expected_tokens:
        actual_token = lexer.token()
        assert expected_token[0] == actual_token.type and expected_token[1] == actual_token.value,\
            'Expected = {}; Actual = {};'.format(expected_token, actual_token)
    extra_token = lexer.token()
    assert extra_token is None, 'Unexpected token: {}'.format(extra_token)


def test_name(lexer):
    data = '''
        aNN_P<Par23k+=_q
    '''
    expected = [('NAME', 'aNN_P'), ('LESS_THAN', '<'), ('NAME', 'Par23k'), ('PLUS', '+'), ('ASSIGNMENT', '='), ('NAME', '_q')]
    test_case(lexer, data, expected)


def test_equals_and_assigment(lexer):
    data = '''
        abyr = valg == dog
    '''
    expected = [('NAME', 'abyr'), ('ASSIGNMENT', '='), ('NAME', 'valg'), ('EQUALS', '=='), ('NAME', 'dog')]
    test_case(lexer, data, expected)


def test_literal_string(lexer):
    data = '''
        a't1'
        "t2"
        '""'
        "''"
    '''
    expected = [('NAME', 'a'), ('LITERAL_STRING', "'t1'"), ('LITERAL_STRING', '"t2"'), ('LITERAL_STRING', "'\"\"'"), ('LITERAL_STRING', '"\'\'"')]
    test_case(lexer, data, expected)


def test_number(lexer):
    data = '''
        a2.3
        .11
        2.
        3
        .
    '''
    expected = [('NAME', 'a2'), ('NUMBER', .3), ('NUMBER', .11), ('NUMBER', 2.), ('NUMBER', 3), ('DOT', '.')]
    test_case(lexer, data, expected)


def test_tokens_in_string(lexer):
    data = '''
        ['[\[]']
    '''
    expected = [('SQUARE_LBRACKET', '['), ('LITERAL_STRING', "'[\[]'"), ('SQUARE_RBRACKET', ']')]
    test_case(lexer, data, expected)


def test_nil_true_false(lexer):
    data = '''
        nil true false
    '''
    expected = [('NIL', None), ('TRUE', True),  ('FALSE', False)]
    test_case(lexer, data, expected)


def test_dot_concat_vararg(lexer):
    data = '''
        a.b..c...d..e
    '''
    expected = [('NAME', 'a'), ('DOT', '.'), ('NAME', 'b'), ('CONCAT', '..'), ('NAME', 'c'),
                ('VARARG', '...'), ('NAME', 'd'), ('CONCAT', '..'), ('NAME', 'e')]
    test_case(lexer, data, expected)


def test_bitwise_ops(lexer):
    data = '''
        ~a|b&c
    '''
    expected = [('BITWISE_NOT', '~'), ('NAME', 'a'), ('BITWISE_OR', '|'), ('NAME', 'b'), ('BITWISE_AND', '&'),
                ('NAME', 'c')]
    test_case(lexer, data, expected)


def test_not_equals_bitwise_not(lexer):
    data = '''
        a~=b
        a~b
    '''
    expected = [('NAME', 'a'), ('NOT_EQUALS', '~='), ('NAME', 'b'), ('NAME', 'a'), ('BITWISE_NOT', '~'), ('NAME', 'b')]
    test_case(lexer, data, expected)


def test_keywords(lexer):
    data = '''
        local function a()
            return  {['b'] = c};
    '''
    expected = [('LOCAL', 'local'), ('FUNCTION', 'function'), ('NAME', 'a'), ('ROUND_LBRACKET', '('), ('ROUND_RBRACKET', ')'),
                ('RETURN', 'return'), ('LBRACE', '{'), ('SQUARE_LBRACKET', '['), ('LITERAL_STRING', "'b'"), ('SQUARE_RBRACKET', ']'),
                ('ASSIGNMENT', '='), ('NAME', 'c'), ('RBRACE', '}'), ('SEMICOLON', ';')]
    test_case(lexer, data, expected)


def test():
    lexer = lex.lex(module=lua_lexer_rules)

    test_name(lexer)
    test_equals_and_assigment(lexer)
    test_literal_string(lexer)
    test_number(lexer)
    test_tokens_in_string(lexer)
    test_nil_true_false(lexer)
    test_dot_concat_vararg(lexer)
    test_bitwise_ops(lexer)
    test_not_equals_bitwise_not(lexer)
    test_keywords(lexer)


if __name__ == '__main__':
    test()
