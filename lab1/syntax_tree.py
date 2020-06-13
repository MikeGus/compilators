from collections import deque


def is_operator(char):
    return char in '|*.'


class SyntaxNode:
    def __init__(self, symbol, position=None, left=None, right=None, nullable=None, firstpos=None, lastpos=None):
        self.symbol = symbol
        self.position = position
        self.left = left
        self.right = right
        self.nullable = nullable
        self.firstpos = firstpos
        self.lastpos = lastpos
        self.followpos = set()

    def __str__(self):
        return '{}s: {}; p: {}, n: {}, f: {}, l: {}, follow: {}\n{}'.format(
            self.left if self.left is not None else '',
            self.symbol,
            self.position,
            self.nullable,
            self.firstpos,
            self.lastpos,
            self.followpos,
            self.right if self.right is not None else '',
        )


class SyntaxTree:
    # '#' expected at the end of regexp, '|', '*', '.', '#' should be escaped
    def __init__(self, postfix_regexp):
        self.position_nodes = []
        followpos_nodes = []
        stack = deque()
        skip_next = False
        postfix_regexp += '#'  # meaningless character for next loop
        current_position = 0
        for current_char, next_char in zip(postfix_regexp[:-1], postfix_regexp[1:]):
            if skip_next:
                skip_next = False
                continue
            if current_char == '\\':
                current_char = next_char
                skip_next = True
            if not is_operator(current_char) or skip_next:
                stack.append(
                    SyntaxNode(
                        current_char,
                        position=current_position,
                        left=None,
                        right=None,
                        nullable=False,
                        firstpos=set([current_position]),
                        lastpos=set([current_position])
                    )
                )
                self.position_nodes.append(stack[-1])
                current_position += 1
            elif current_char == '|':
                right_node = stack.pop()
                left_node = stack.pop()
                stack.append(
                    SyntaxNode(
                        current_char,
                        position=None,
                        left=left_node,
                        right=right_node,
                        nullable=left_node.nullable or right_node.nullable,
                        firstpos=left_node.firstpos.union(right_node.firstpos),
                        lastpos=left_node.firstpos.union(right_node.firstpos)
                    )
                )
            elif current_char == '.':
                right_node = stack.pop()
                left_node = stack.pop()
                stack.append(
                    SyntaxNode(
                        current_char,
                        position=None,
                        left=left_node,
                        right=right_node,
                        nullable=left_node.nullable and right_node.nullable,
                        firstpos=left_node.firstpos.union(right_node.firstpos) if left_node.nullable else left_node.firstpos,
                        lastpos=left_node.firstpos.union(right_node.firstpos) if right_node.nullable else right_node.lastpos
                    )
                )
                followpos_nodes.append(stack[-1])
            elif current_char == '*':
                right_node = stack.pop()
                stack.append(
                    SyntaxNode(
                        current_char,
                        position=None,
                        left=None,
                        right=right_node,
                        nullable=True,
                        firstpos=right_node.firstpos,
                        lastpos=right_node.lastpos
                    )
                )
                followpos_nodes.append(stack[-1])
        self.root = stack.pop()
        for node in followpos_nodes:
            if node.symbol == '.':
                for position in node.left.lastpos:
                    self.position_nodes[position].followpos = self.position_nodes[position].followpos.union(node.right.firstpos)
            elif node.symbol == '*':
                for position in node.right.lastpos:
                    self.position_nodes[position].followpos = self.position_nodes[position].followpos.union(node.right.firstpos)

    def __str__(self):
        return 'Root Symbol: {}\n{}'.format(self.root.symbol, str(self.root))


if __name__ == '__main__':
    s = 'ab|*a.b.b.#.'
    tree = SyntaxTree(s)
    print(tree)
