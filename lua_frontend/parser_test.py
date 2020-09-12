import json

import ply.lex as lex
import ply.yacc as yacc

import lua_lexer_rules
import lua_parser


def check_ast(expected, actual):
    assert isinstance(actual, expected.__class__), 'Expected class {} != actual class {}\n{}\n{}\n'.format(expected.__class__, actual.__class__, expected, actual)
    if isinstance(actual, dict):
        extra_keys = set(expected.keys()).difference(set(actual.keys()))
        assert not extra_keys, 'Expected extra keys {} in node  {}'.format(extra_keys, actual)
        for exp_k, exp_v in expected.items():
            act_v = actual[exp_k]
            check_ast(exp_v, act_v)
    elif isinstance(actual, list):
        assert len(expected) == len(actual), 'Expected length {} != actual length {}'.format(len(expected), len(actual))
        for exp_el, act_el in zip(expected, actual):
            check_ast(exp_el, act_el)
    else:
        assert expected == actual, 'Expected value {} != actual value {}'.format(expected, actual)


def test_case(parser, lexer, data, expected_statements):
    expected_ast = {
        'node_type': 'Chunk',
        'block': {
            'node_type': 'Block',
            'statements': {
                'node_type': 'StatementList',
                'statements': expected_statements
            }
        }
    }
    ast_raw = parser.parse(data, lexer=lexer)
    actual_ast = json.loads(str(ast_raw))
    check_ast(expected_ast, actual_ast)


def test_assignment(parser, lexer):
    data = '''
        q, b = nil, true
    '''
    expected_statements = [{
        'node_type': 'Statement',
        'statement': {
            'node_type': 'Assignment',
            'variables': {
                'node_type': 'VariableList',
                'variables': [{
                    'node_type': 'Variable',
                    'identifier': {
                        'node_type': 'Name',
                        'name': 'q',
                    }
                }, {
                    'node_type': 'Variable',
                    'identifier': {
                        'node_type': 'Name',
                        'name': 'b',
                    }
                }]
            },
            'expressions': {
                'node_type': 'ExpressionList',
                'expressions': [{
                    'node_type': 'Expression',
                }, {
                    'node_type': 'Expression',
                    'expression': True,
                }]
            }
        }
    }]
    test_case(parser, lexer, data, expected_statements)


def test_binary_operation_priority(parser, lexer):
    data = '''
        print(- b + a * 2)
    '''
    expected_statements = [{
        'node_type': 'Statement',
        'statement': {
            'node_type': 'FunctionCall',
            'args': {
                'node_type': 'Args',
                'args': {
                    'expressions': [{
                        'node_type': 'Expression',
                        'expression': {
                            'node_type': 'BinaryOperation',
                            'left': {
                                'node_type': 'Expression',
                                'expression': {
                                    'node_type': 'UnaryOperation',
                                    'expression': {
                                        'node_type': 'Expression',
                                        'expression': {
                                            'node_type': 'PrefixExpression',
                                            'expression': {
                                                'node_type': 'Variable',
                                                'identifier': {
                                                    'node_type': 'Name',
                                                    'name': 'b'
                                                }
                                            }
                                        }
                                    },
                                    'operation': '-'
                                },
                            },
                            'right': {
                                'node_type': 'Expression',
                                'expression': {
                                    'node_type': 'BinaryOperation',
                                    'left': {
                                        'expression': {
                                            'node_type': 'PrefixExpression',
                                            'expression': {
                                                'node_type': 'Variable',
                                                'identifier': {
                                                    'node_type': 'Name',
                                                    'name': 'a',
                                                }
                                            }
                                        }
                                    },
                                    'right': {
                                        'expression': {
                                            'node_type': 'Number',
                                            'value': 2.0,
                                        }
                                    },
                                    'operation': '*',
                                }
                            },
                            'operation': '+',
                        }
                    }]
                }
            }
        }
    }]
    test_case(parser, lexer, data, expected_statements)


def test_binary_operation_priority_override(parser, lexer):
    data = '''
        print((b + a) * 2)
    '''
    expected_statements = [{
        'node_type': 'Statement',
        'statement': {
            'node_type': 'FunctionCall',
            'args': {
                'node_type': 'Args',
                'args': {
                    'expressions': [{
                        'node_type': 'Expression',
                        'expression': {
                            'node_type': 'BinaryOperation',
                            'left': {
                                'node_type': 'Expression',
                                'expression': {
                                    'node_type': 'PrefixExpression',
                                    'expression': {
                                        'node_type': 'Expression',
                                        'expression': {
                                            'node_type': 'BinaryOperation',
                                            'operation': '+',
                                            'left': {
                                                'node_type': 'Expression',
                                                'expression': {
                                                    'node_type': 'PrefixExpression',
                                                    'expression': {
                                                        'node_type': 'Variable',
                                                        'identifier': {
                                                            'node_type': 'Name',
                                                            'name': 'b',
                                                        }
                                                    }
                                                }
                                            },
                                            'right': {
                                                'node_type': 'Expression',
                                                'expression': {
                                                    'node_type': 'PrefixExpression',
                                                    'expression': {
                                                        'node_type': 'Variable',
                                                        'identifier': {
                                                            'node_type': 'Name',
                                                            'name': 'a',
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            'right': {
                                'node_type': 'Expression',
                                'expression': {
                                    'node_type': 'Number',
                                    'value': 2.0,
                                }
                            },
                            'operation': '*',
                        }
                    }]
                }
            }
        }
    }]
    test_case(parser, lexer, data, expected_statements)


def test_table(parser, lexer):
    data = '''
        b = {[a] = 3,  krya =  4, 5}
    '''
    expected_statements = [{
        'node_type': 'Statement',
        'statement': {
            'node_type': 'Assignment',
            'variables': {
                'node_type': 'VariableList',
                'variables': [{
                    'node_type': 'Variable',
                    'identifier': {
                        'node_type': 'Name',
                        'name': 'b',
                    }
                }]
            },
            'expressions': {
                'node_type': 'ExpressionList',
                'expressions': [{
                    'node_type': 'Expression',
                    'expression': {
                        'node_type': 'TableConstructor',
                        'fieldlist': {
                            'node_type':  'FieldList',
                            'fields': [
                                {
                                    'node_type':  'Field',
                                    'identifier': {
                                        'node_type':  'Expression',
                                        'expression': {
                                            'node_type': 'PrefixExpression',
                                            'expression': {
                                                'node_type': 'Variable',
                                                'identifier': {
                                                    'node_type': 'Name',
                                                    'name': 'a'
                                                }
                                            }
                                        },
                                    },
                                    'value': {
                                        'node_type': 'Expression',
                                        'expression': {
                                            'node_type':  'Number',
                                            'value': 3.0,
                                        }
                                    }
                                },
                                {
                                    'node_type':  'Field',
                                    'identifier': {
                                        'node_type': 'Name',
                                        'name': 'krya'
                                    },
                                    'value': {
                                        'node_type': 'Expression',
                                        'expression': {
                                            'node_type':  'Number',
                                            'value': 4.0,
                                        }
                                    }
                                },
                                {
                                    'node_type':  'Field',
                                    'value': {
                                        'node_type': 'Expression',
                                        'expression': {
                                            'node_type':  'Number',
                                            'value': 5.0,
                                        }
                                    }
                                },
                            ]
                        }
                    }
                }]
            }
        }
    }]
    test_case(parser, lexer, data, expected_statements)


def test_loop(parser, lexer):
    data = '''
        while 3 ~= 4 do
            a = 3
        end
    '''
    expected_statements = [{
        'node_type': 'Statement',
        'statement': {
            'node_type': 'WhileLoop',
            'expression': {
                'node_type': 'Expression',
                'expression':  {
                    'node_type': 'BinaryOperation',
                    'left': {
                        'expression': {
                            'node_type': 'Number',
                            'value': 3.0,
                        }
                    },
                    'right': {
                        'expression': {
                            'node_type': 'Number',
                            'value': 4.0,
                        }
                    },
                    'operation':  '~=',
                }
            },
            'block': {
                'node_type': 'Block',
                'statements': {
                    'node_type': 'StatementList',
                    'statements': [{
                        'node_type': 'Statement',
                        'statement': {
                            'node_type': 'Assignment',
                            'variables': {
                                'node_type': 'VariableList',
                                'variables': [{
                                    'node_type': 'Variable',
                                    'identifier': {
                                        'node_type': 'Name',
                                        'name': 'a',
                                    }
                                }]
                            },
                            'expressions': {
                                'node_type': 'ExpressionList',
                                'expressions': [{
                                    'node_type': 'Expression',
                                    'expression': {
                                        'node_type': 'Number',
                                        'value': 3.0,
                                    }
                                }]
                            }
                        }
                    }]
                }
            }
        }
    }]
    test_case(parser, lexer, data, expected_statements)


def test():
    lexer = lex.lex(module=lua_lexer_rules)
    parser = yacc.yacc(module=lua_parser)

    test_assignment(parser, lexer)
    # test_binary_operation_priority(parser, lexer)
    # test_binary_operation_priority_override(parser, lexer)
    # test_table(parser, lexer)
    # test_loop(parser, lexer)


if __name__ == '__main__':
    test()
