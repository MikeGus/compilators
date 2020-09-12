import ply.lex as lex

import lua_lexer_rules


def test_case(lexer, data, expected_tokens):
    lexer.input(data)
    for expected_token in expected_tokens:
        actual_token = lexer.token()
        assert expected_token == actual_token, 'Expected = {}; Actual = {};'.format(expected_token, actual_token)
    extra_token = lexer.token()
    assert extra_token is None, 'Unexpected token: {}'.format(extra_token)


def test():
    data = '''
        3 + 4 * 10
        + -20 *2
    '''
    lexer = lex.lex(module=lua_lexer_rules)
    test_case(lexer, data, [])


if __name__ == '__main__':
    test()
