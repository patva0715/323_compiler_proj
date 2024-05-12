import sys


class FSM:
    def __init__(self, *, matrix, transition_function, accepting_states, init_state):
        # Initialize the FSM with its state transition matrix, transition function,
        # set of accepting states, and initial state.
        self.init_state = self.state = init_state
        self.matrix = matrix
        self.transition_function = transition_function
        self.accepting_states = accepting_states

    def transition(self, input):
        # Change the FSM's current state based on the input character and the transition function.
        self.state = self.transition_function(input, self.matrix, self.state)

    def is_accepting(self):
        # Check if the FSM's current state is one of the accepting states.
        return self.state in self.accepting_states

    def reset(self):
        # Reset the FSM to its initial state.
        self.state = self.init_state


def lexical_analyzer(input_file):
    # if len(sys.argv) != 3:
    #     print("Usage: python3 script.py <input_file> <output_file>")
    # sys.exit(1)

    # Define the sets of keywords, operators, separators, and compound operators for the lexical analysis.
    KEYWORDS = {"function", "return", "else", "if", "while", "endwhile",
                "integer", "double", "boolean", "real", "true", "false",
                "scan", "endif","print",}
    OPERATORS = {"+", "-", "*", "/", "=", "<", ">"}
    SEPARATORS = {";", "(", ")", "$", ",", "{", "}"}
    COMPOUND_OPERATORS = {"<=", ">=", "==","!="}

    # Initialize FSMs for real numbers, integers, and identifiers with their respective
    # state transition matrices, transition functions, and accepting states.
    real_FSM = FSM(
        matrix=[
            [1, 4, 4],
            [1, 2, 4],
            [3, 4, 4],
            [3, 4, 4],
            [4, 4, 4],
        ],
        transition_function=lambda x, y, z: y[z][0] if x.isdigit() else (y[z][1] if x == '.' else y[z][2]),
        accepting_states={3},
        init_state=0
    )
    integer_FSM = FSM(
        matrix=[
            [1, 2],
            [1, 2],
            [2, 2]
        ],
        transition_function=lambda x, y, z: y[z][0] if x.isdigit() else y[z][1],
        accepting_states={1},
        init_state=0
    )
    id_FSM = FSM(
        matrix=[
            [1, 2, 2, 2],
            [1, 1, 1, 2],
            [2, 2, 2, 2],
        ],
        transition_function=lambda x, y, z: y[z][0] if x.isalpha() else (y[z][1] if x.isdigit() else (y[z][2] if x == '_' else y[z][3])),
        accepting_states={1},
        init_state=0
    )
    # Star
    # Initialize a list to hold the tokens identified in the input file.
    tokens = []
    
    with open(input_file, 'r') as inputFile:
        # Read the entire input file and append " END" to mark the end of the file.
        file = inputFile.read() + " END"
        i = 0

    current_lexeme = ""

    while i < len(file):
        # Check for comments starting with "[* " and skip them.
        if file[i] == "[" and file[i:i+3] == "[* ":
            end_comment = file.find(" *]", i)
            if end_comment == -1:
                break  # Break if the comment is not properly closed.
            i = end_comment + 3  # Move the index past the closing "*]"
            continue

        # Process characters that are operators, separators, or whitespace.
        if file[i] in SEPARATORS.union(OPERATORS).union({" ","\n","!"}):
            # Evaluate the current_lexeme using the FSMs to determine the token type.
            if file[i] != "!":
                if current_lexeme in KEYWORDS:
                    tokens.append(("Keyword", current_lexeme))
                    current_lexeme = file[i]
                elif integer_FSM.is_accepting():
                    tokens.append(("Integer", current_lexeme))
                elif real_FSM.is_accepting():
                    tokens.append(("Real", current_lexeme))
                elif id_FSM.is_accepting():
                    tokens.append(("Identifier", current_lexeme))
                else:
                    # If the lexeme does not match any valid token type, mark it as invalid.
                    if current_lexeme not in SEPARATORS and current_lexeme != "":
                        tokens.append(("Invalid", current_lexeme))

            # Handle operators, possibly checking for compound operators.

            if file[i] in OPERATORS.union({"!"}):
                compound_operator = file[i] + file[i + 1] if i + 1 < len(file) else ""
                if compound_operator in COMPOUND_OPERATORS:
                    tokens.append(("Operator", compound_operator))
                    i += 1  # Increment index to skip the next character, part of the compound operator.
                else: tokens.append(("Operator", file[i]))
            
            # Handle separators.
            if file[i] in SEPARATORS:
                tokens.append(("Separator", file[i]))

            # Reset the FSMs for the next lexeme.
            current_lexeme = ""
            id_FSM.reset()
            real_FSM.reset()
            integer_FSM.reset()

        else:
            # If the character is not an operator, separator, or whitespace, add it to the current lexeme
            # and feed it into the FSMs to update their states.
            current_lexeme += file[i]
            id_FSM.transition(file[i])
            real_FSM.transition(file[i])
            integer_FSM.transition(file[i])

        i += 1  # Move to the next character in the file.

    # Write the identified tokens to the output file.
    return tokens


