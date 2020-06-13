from collections import namedtuple, deque
from notation_converter import NotationConverter, Operator
from preprocessing import add_concatenation
from string import ascii_lowercase, ascii_uppercase
from syntax_tree import SyntaxTree


TransitionKey = namedtuple('TransitionKey', ['state', 'symbol'])


class DFA:
    # '|', '*', '.', '(', ')', '#', '\' should be escaped with '\'
    def __init__(self, alphabet, regexp):
        self.alphabet = alphabet
        replenished_regexp = regexp + '#'
        preprocessed_regexp = add_concatenation(replenished_regexp + '', '.', lambda x: x.isalpha() or x in ')*#', lambda x: x.isalpha() or x in '(#')

        operators = [
            Operator(operator, priority)
            for operator, priority in (('*', 2), ('.', 1), ('|', 0))
        ]
        converter = NotationConverter(operators)

        postfix_regexp = converter.infix_to_postfix(preprocessed_regexp)

        self.states = set()
        self.initial_state = None
        self.transitions = {}
        self.final_states = set()

        unmarked_states = set()
        syntax_tree = SyntaxTree(postfix_regexp)
        self.initial_state = frozenset(syntax_tree.root.firstpos)
        unmarked_states.add(self.initial_state)
        while unmarked_states:
            unmarked_state = unmarked_states.pop()
            self.states.add(unmarked_state)
            symbol_positions = {}
            for position in unmarked_state:
                symbol = syntax_tree.position_nodes[position].symbol
                if symbol not in symbol_positions:
                    symbol_positions[symbol] = set([position])
                else:
                    symbol_positions[symbol].add(position)
            for symbol, positions in symbol_positions.items():
                follow_positions = set()
                for position in positions:
                    follow_positions = follow_positions.union(syntax_tree.position_nodes[position].followpos)
                new_state = frozenset(follow_positions)
                if new_state not in self.states:
                    unmarked_states.add(new_state)
                self.transitions[TransitionKey(unmarked_state, symbol)] = new_state
        hash_position = syntax_tree.position_nodes[-1].position
        for state in self.states:
            if hash_position in state:
                self.final_states.add(state)

        # remove traces of '#'
        self.states.remove(frozenset())
        keys_to_remove = [key for key, value in self.transitions.items() if value == frozenset()]
        for key in keys_to_remove:
            self.transitions.pop(key)

        self.fake_state = frozenset()
        self.states.add(self.fake_state)
        for state in self.states:
            for symbol in self.alphabet:
                key = TransitionKey(state, symbol)
                if key not in self.transitions:
                    self.transitions[key] = self.fake_state
        for symbol in self.alphabet:
            self.transitions[TransitionKey(self.fake_state, symbol)] = self.fake_state

    def _get_reachable_states(self, states_map):
        reachable_states = [False] * (len(self.states) + 1)
        marked_states = set()
        stack = deque()
        stack.append(self.initial_state)
        while stack:
            current_state = stack.pop()
            marked_states.add(current_state)
            unmarked_states = set([
                self.transitions[transition_key]
                for transition_key in self.transitions
                if self.transitions[transition_key] not in marked_states
            ])
            stack.extend(unmarked_states)

        for state in marked_states:
            state_idx = states_map[state]
            reachable_states[state_idx] = True
        return reachable_states

    def _get_inequality_matrix(self, states_number, final_states, reverse_edges):
        inequality_matrix = []
        for i in range(states_number):
            inequality_matrix.append([False] * states_number)
        queue = deque()
        for i in range(states_number):
            for j in range(states_number):
                if not inequality_matrix[i][j] and (i in final_states) is not (j in final_states):
                    inequality_matrix[i][j] = inequality_matrix[j][i] = True
                    queue.appendleft([i, j])

        while queue:
            i, j = queue.pop()
            for symbol in self.alphabet:
                for r in reverse_edges[i][symbol]:
                    for s in reverse_edges[j][symbol]:
                        if not inequality_matrix[r][s]:
                            inequality_matrix[r][s] = inequality_matrix[s][r] = True
                            queue.append([r, s])

        return inequality_matrix

    def minimize(self):
        states_map = {
            state: idx + 1
            for idx, state in enumerate(self.states.difference(set([self.fake_state])))
        }
        states_map[self.fake_state] = 0
        reachable_states = self._get_reachable_states(states_map)
        states_number = len(states_map)
        reverse_edges = []
        for i in range(states_number):
            reverse_edges.append({
                symbol: set()
                for symbol in self.alphabet
            })
        final_states = [states_map[state] for state in self.final_states]
        for transition_key, destination in self.transitions.items():
            destination_idx = states_map[destination]
            reverse_edges[destination_idx][transition_key.symbol].add(states_map[transition_key.state])

        inequality_matrix = self._get_inequality_matrix(states_number, final_states, reverse_edges)

        component = [-1] * states_number
        for i in range(states_number):
            if not inequality_matrix[0][i]:
                component[i] = 0

        components_count = 0
        for i in range(1, states_number):
            if reachable_states[i] and component[i] == -1:
                components_count += 1
                component[i] = components_count
                for j in range(i + 1, states_number):
                    if not inequality_matrix[i][j]:
                        component[j] = components_count

        self.states = set([
            i for i in range(1, components_count + 1)
        ])
        self.initial_state = component[states_map[self.initial_state]]
        new_final_states = set([
            component[states_map[state]]
            for state in self.final_states
        ])
        self.final_states = new_final_states
        new_transitions = {
            TransitionKey(component[states_map[transition_key.state]], transition_key.symbol): component[states_map[destination]]
            for transition_key, destination in self.transitions.items()
            if transition_key.state != self.fake_state and destination != self.fake_state
        }
        self.transitions = new_transitions

    def simulate(self, text):
        current_state = self.initial_state
        for symbol in text:
            if current_state in self.final_states:
                return True
            current_state = self.transitions.get(TransitionKey(current_state, symbol))
            if current_state is None:
                return False
        return current_state in self.final_states

    def __str__(self):
        return 'Alphabet:\n{}\nStates:\n{}\nInitial state:\n{}\nTransitions:\n{}\nFinal states:\n{}\n'.format(
            self.alphabet,
            self.states,
            self.initial_state,
            "\n".join(['{} + {} -> {}'.format(key.state, key.symbol, value) for key, value in self.transitions.items()]),
            self.final_states
        )


if __name__ == '__main__':
    regexp = '(a|b)*abb'
    dfa = DFA(set(list(ascii_lowercase) + list(ascii_uppercase)), regexp)
    print('Regexp: ', regexp)
    # print('DFA: ', str(dfa))
    dfa.minimize()
    print('Minimized DFA:\n', str(dfa))
    for s in ['abb', 'abbbaaaaaababba', 'sfasfas', 'abbknsjd', 'krya']:
        print('Input: {}; Output: {}'.format(s, dfa.simulate(s)))
