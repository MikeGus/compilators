def add_concatenation(text, concatenation_symbol, in_alphabet_1, in_alphabet_2):
    if len(text) <= 1:
        return text
    result = ''
    for current_char, next_char in zip(text[:-1], text[1:]):
        result += current_char
        if in_alphabet_1(current_char) and in_alphabet_2(next_char):
            result += concatenation_symbol
    result += text[-1]
    return result


if __name__ == '__main__':
    text = 'abc(ab|bc)*((ac|bc)(a|b))*'
    print('Before: {}'.format(text))
    print('After: {}'.format(add_concatenation(text, '.', lambda x: x.isalpha() or x in ')*#', lambda x: x.isalpha() or x in '(#')))
