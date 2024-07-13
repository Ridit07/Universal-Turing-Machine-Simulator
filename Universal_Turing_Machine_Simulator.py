import json

class State:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, State) and self.name == other.name

    def __hash__(self):
        
        return hash(self.name)
    
def binary_encode_state(state):
    return bin(int(state[1:]))[2:]

def binary_encode_symbol(symbol):
    if symbol == '0':
        return '0'
    elif symbol == '1':
        return '1'
    elif symbol == 'B':
        return '10'  

def print_transition_hash_map_binary(tm_description):
    transition_map = {}

    for transition in tm_description.transitions:
        key = (binary_encode_state(transition.current_state.name), binary_encode_symbol(transition.current_symbol))
        value = {
            "next_state": binary_encode_state(transition.next_state.name),
            "write_symbol": binary_encode_symbol(transition.write_symbol),
            "move": transition.move
        }

        transition_map[key] = value

    for key, value in transition_map.items():
        print(f"Current State: {key[0]}, Read Symbol: {key[1]} => Next State: {value['next_state']}, Write Symbol: {value['write_symbol']}, Move: {value['move']}")


def print_transition_hash_map(tm_description):
    transition_map = {}
    
    for transition in tm_description.transitions:
        key = (transition.current_state.name, transition.current_symbol)
        value = {
            "next_state": transition.next_state.name,
            "write_symbol": transition.write_symbol,
            "move": transition.move
        }
        
        transition_map[key] = value
    
    for key, value in transition_map.items():
        print(f"Current State: {key[0]}, Read Symbol: {key[1]} => Next State: {value['next_state']}, Write Symbol: {value['write_symbol']}, Move: {value['move']}")




class Transition:
    def __init__(self, current_state, current_symbol, next_state, write_symbol, move):
        self.current_state = current_state
        self.current_symbol = current_symbol
        self.next_state = next_state
        self.write_symbol = write_symbol
        self.move = move

class TuringMachineDescription:
    def __init__(self, transitions, start_state, accept_states, reject_states):
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states
        self.reject_states = reject_states

    def to_dict(self):
        return {
            "transitions": [(t.current_state.name, t.current_symbol, t.next_state.name, t.write_symbol, t.move) for t in self.transitions],
            "start_state": self.start_state.name,
            "accept_states": [state.name for state in self.accept_states],
            "reject_states": [state.name for state in self.reject_states]
        }

    @staticmethod
    def from_dict(description_dict):
        transitions = []
        for t in description_dict["transitions"]:
            current_state = State(t[0])
            next_state = State(t[2])
            transitions.append(Transition(current_state, t[1], next_state, t[3], t[4]))
        start_state = State(description_dict["start_state"])
        accept_states = {State(state) for state in description_dict["accept_states"]}
        reject_states = {State(state) for state in description_dict["reject_states"]}
        return TuringMachineDescription(transitions, start_state, accept_states, reject_states)

    def __str__(self):
        return str(self.to_dict())


class TuringMachine:
    def __init__(self, initial_tape, description):
        self.tape = list(initial_tape) + ['B']
        self.head = 0
        self.current_state = description.start_state
        self.transitions = description.transitions
        self.accept_states = description.accept_states
        self.reject_states = description.reject_states

    def step(self):
        if self.head < 0:
            self.tape.insert(0, 'B')
            self.head = 0

        current_symbol = self.tape[self.head]
        for transition in self.transitions:
            if transition.current_state == self.current_state and transition.current_symbol == current_symbol:
                self.tape[self.head] = transition.write_symbol
                self.current_state = transition.next_state
                if transition.move == 'R':
                    self.head += 1
                elif transition.move == 'L':
                    self.head -= 1
                return

        if self.current_state not in self.reject_states:
            self.reject_states.add(self.current_state)
        self.current_state = 'Reject'

    def run(self):
        while self.current_state not in self.accept_states.union(self.reject_states):
            self.step()
        return self.current_state in self.accept_states

class TuringMachineDescriptionEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, State):
            return obj.name
        elif isinstance(obj, Transition):
            return {
                "current_state": obj.current_state.name,
                "current_symbol": obj.current_symbol,
                "next_state": obj.next_state.name,
                "write_symbol": obj.write_symbol,
                "move": obj.move
            }
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, TuringMachineDescription):
            return obj.to_dict()
        return super().default(obj)
def turing_machine_description_decoder(obj):
    if 'transitions' in obj:
        transitions = []
        for t in obj['transitions']:
            current_state = State(t[0])
            next_state = State(t[2])
            transitions.append(Transition(current_state, t[1], next_state, t[3], t[4]))
        start_state = State(obj["start_state"])
        accept_states = {State(state) for state in obj["accept_states"]}
        reject_states = {State(state) for state in obj["reject_states"]}
        return TuringMachineDescription(transitions, start_state, accept_states, reject_states)
    return obj

class UniversalTuringMachine:
    def __init__(self, tm_description, initial_tape):
        self.description = tm_description
        self.tm = TuringMachine(initial_tape, tm_description)

    def run(self):
        return self.tm.run()

    def encode_description(self):
        return json.dumps(self.description, cls=TuringMachineDescriptionEncoder)

    @staticmethod
    def decode_description(encoded_description):
        return json.loads(encoded_description, object_hook=turing_machine_description_decoder)

def print_machine_details(tm_description):
    print("Start State:", tm_description.start_state.name)
    print("Accept States:", [state.name for state in tm_description.accept_states])
    # print("Reject States:", [state.name for state in tm_description.reject_states])
    # print("Transitions:")
    # for t in tm_description.transitions:
    #     print(f"  From {t.current_state.name} on '{t.current_symbol}' to {t.next_state.name}, write '{t.write_symbol}', move {t.move}")
    print()

tm_description = TuringMachineDescription(
    [
        Transition(State('Q0'), '0', State('Q1'), 'B', 'R'),
        Transition(State('Q0'), 'B', State('Q5'), 'B', 'R'),
        Transition(State('Q1'), '0', State('Q2'), 'B', 'R'),
        Transition(State('Q2'), '0', State('Q2'), '0', 'R'),
        Transition(State('Q2'), '1', State('Q2'), '1', 'R'),
        Transition(State('Q2'), 'B', State('Q3'), 'B', 'L'),
        Transition(State('Q3'), '1', State('Q4'), 'B', 'L'),
        Transition(State('Q4'), '0', State('Q4'), '0', 'L'),
        Transition(State('Q4'), '1', State('Q4'), '1', 'L'),
        Transition(State('Q4'), 'B', State('Q0'), 'B', 'R')
    ],
    State('Q0'),
    {State('Q5')},
    {State('Reject')}
)

print_machine_details(tm_description)

input_tape = ""
utm = UniversalTuringMachine(tm_description, input_tape)

encoded_description = utm.encode_description()
print("Encoded description:", encoded_description)

print_transition_hash_map_binary(tm_description)


decoded_description = UniversalTuringMachine.decode_description(encoded_description)
print("Decoded description:", decoded_description)
print()
print()
result = utm.run()
print("Accepted" if result else "Rejected")
print()
print()
print_transition_hash_map(tm_description)

