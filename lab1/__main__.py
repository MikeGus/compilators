from dfa import DFA

TEST_REGEXPS = {
    'a': {
        'b': False,
        'a': True,
        'bbba': False,
        'bbc': False,
        'aaab': True,
    },
    'a*': {
        'bbbab': True,
        'a': True,
        '': True,
        'aaaa': True,
        'ab': True,
    },
    'a|b': {
        'a': True,
        '': False,
        'b': True,
        'c': False,
    },
    'ab': {
        'a': False,
        'b': False,
        'ab': True,
        '': False,
        'abcde': True,
    },
    '(a|b)*': {
        'a': True,
        'b': True,
        'aaaa': True,
        'bbbb': True,
        '': True,
        'bababbbaa': True,
        'bbabaabddss': True,
    },
    '(ab)*': {
        '': True,
        'ab': True,
        'a': True,
        'babababababa': True,
        'abababababab': True,
        'abc': True,
    },
    'ab*': {
        '': False,
        'b': False,
        'a': True,
        'ac': True,
        'ab': True,
        'abbbbc': True,
    },
    'aab*(a|b)*b(b*c)': {
        'aabc': True,
        'abc': False,
        '': False,
        'aabbbbbaaaaabbbbbbbb': False,
        'aabbbbbaaaaabbbbbbbbc': True,
        'aabbbbbaaaaabbbbbbbbcc': True,
        'aaaaaaaabc': True,
        'aaaaaac': False,
    },
    '(a|b)b*(c|d)*': {
        'a': True,
        '': False,
        'b': True,
        'bbbbbb': True,
        'cccc': False,
        'ad': True,
        'aq': True,
    },
}


def setup_test(regexp):
    dfa = DFA(regexp)
    dfa.minimize()
    return dfa


def test(dfa, expected, terminals):
    actual = dfa.simulate(terminals)
    assert expected is actual, 'expected = {}, actual = {}'.format(expected, actual)


def main():
    print('TESTING')
    for test_regexp, test_cases in TEST_REGEXPS.items():
        print('REGEXP: {}'.format(test_regexp))
        dfa = setup_test(test_regexp)
        for terminals, expected_result in test_cases.items():
            print('\tTERMINALS: \'{}\', EXPECTED: {}'.format(terminals, expected_result))
            test(dfa, expected_result, terminals)
            print('\tPASSED')
    '''
    expected_responses = [
        [False, True, False, False, False, False, False, False],
        [True, True, True, False, False, True, True, False],
    ]
    for regexp, expected in zip(['ab', '(a|b)b*(c|d)*'], expected_responses):
        # print('Regexp: ', regexp)
        dfa = DFA(regexp)
        dfa.minimize()
        # print('DFA:\n', dfa)
        for s, e_r in zip(['a', 'ab', 'baaabbbbbbccdd', 'dddd', 'dddaa', 'bd', 'b', ''], expected):
            dfa_resp = dfa.simulate(s)
            assert(e_r == dfa_resp)
            # print('String: ', s, ' DFA response: ', dfa_resp, ' Expected: ', e_r)

    regexp = '((ab)|(ab)*)e*f'
    print(regexp)
    dfa = DFA(regexp, set(list('abef')))
    print(dfa)
    dfa.minimize()
    print(dfa)
    s_list = ['abf', 'ab', 'abeef', 'abeee', 'abababf']
    for s in s_list:
        print('str: ', s)
        print('res: ', dfa.simulate(s))
'''


if __name__ == '__main__':
    main()
