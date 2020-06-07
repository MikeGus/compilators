from collections import deque, namedtuple


Operator = namedtuple('Operator', ['symbol', 'priority'])


class NotationConverter:
    def __init__(self, operators):
        self.operators_priority = {
            operator.symbol: operator.priority
            for operator in operators
        }
        self.stack = deque()

    # '\', '(', ')', '.' must be escaped w/ '\'
    def infix_to_postfix(self, text):
        self.stack.clear()
        if len(text) <= 1:
            return text
        text += '#'
        result = ''
        for current_idx, current_char in enumerate(text[:-1]):
            if current_char == '\\':
                current_char += text[current_idx + 1]
            if current_char not in self.operators_priority.keys() and current_char not in '()':
                result += current_char
            elif current_char == '(':
                self.stack.append('(')
            elif current_char == ')':
                while self.stack and self.stack[-1] != '(':
                    result += self.stack.pop()
                if not self.stack:
                    raise ValueError('Invalid parentheses')
                self.stack.pop()
            else:
                while self.stack and self.stack[-1] in self.operators_priority.keys() and self.operators_priority[self.stack[-1]] >= self.operators_priority[current_char]:
                    result += self.stack.pop()
                self.stack.append(current_char)
        while self.stack:
            result += self.stack.pop()
        return result


if __name__ == '__main__':
    operators = [
        Operator(operator, priority)
        for operator, priority in (('*', 2), ('.', 1), ('|', 0))
    ]
    converter = NotationConverter(operators)
    text = 'a.(a|b)*.(a|b)'
    print('Infix: {}'.format(text))
    print('Postfix: {}'.format(converter.infix_to_postfix(text)))
