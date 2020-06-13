from dfa import DFA


def main():
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


if __name__ == '__main__':
    main()
