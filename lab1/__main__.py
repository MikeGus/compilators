from dfa import DFA


def main():
    expected_responses = [
        [False, True, False, False, False, False, False, False],
        [True, True, True, False, False, True, True, False],
    ]
    for regexp, expected in zip(['ab', '(a|b)b*(c|d)*'], expected_responses):
        print('Regexp: ', regexp)
        dfa = DFA(regexp)
        dfa.minimize()
        print('DFA:\n', dfa)
        for s, e_r in zip(['a', 'ab', 'baaabbbbbbccdd', 'dddd', 'dddaa', 'bd', 'b', ''], expected):
            dfa_resp = dfa.simulate(s)
            assert(e_r == dfa_resp)
            print('String: ', s, ' DFA response: ', dfa_resp, ' Expected: ', e_r)


if __name__ == '__main__':
    main()
