from    lexical_analyzer import lexical_analyzer
from util import *
import sys

dict={}
mem_address = 5000
STACK = []
MEMORY = []
inst = [None] *10
instr_address=1

def generate_instruction(op,oprnd):
    try:
        global instr_address
        inst [instr_address]=(instr_address,op,oprnd)
        print(inst)
        instr_address+=1
    except Exception as e:
        print(e)

def get_Address(x):
    return dict[x]

class Instruction:
    def __init__ (self,address,op,oprnd):
        self.address = address
        self.op = op
        self.oprnd=oprnd
        return (self,address,self.op,self.oprnd)

class Lexer:
    def __init__(self, tokens) -> None:
        if len(tokens):
            self.tokens = tokens
            self.curr_index = 0
            self.current = tokens[0]
            self.length = len(tokens)
            with open("tokens.txt", 'w') as file:
                for x in tokens:
                    file.write(str(x)+'\n')
                file.close()
        else:
            self.current = None
            self.curr_index = None
            self.length = 0
    def goNext(self):
        if self.curr_index+1 < self.length:
            self.curr_index += 1
            self.current = self.tokens[self.curr_index]
            return self.current_token_header()
        else:
            self.current = ("End Marker","%$END%$")
            return ("End Marker","%$END%$")
    def goBack(self,num):
        self.curr_index-=1
        self.current=self.tokens[self.curr_index]
    def getCurrent(self):
        return self.current
    def current_token_header(self):
        # For Green and Bold text
        # return f"\033\033[92mToken: {self.current[0]}\033[0m".ljust(37)+f"\033\033[92mLexeme: {self.current[1]}\033[0m \n"
        # For Regular Text
        return f"Token: {self.current[0]}".ljust(33)+f"Lexeme: {self.current[1]}\n"


def rat24s(lex):
    output=lex.current_token_header()
    output+="<Rat24S> -> $ <Opt Function Definitions>  $ <Opt Declaration List>  $ <Statement List>  $\n"
    try:
        current = lex.current
        if current[1] != "$":
            raise Exception(f"Error in rat24s - Expected $ separator but encountered {lex.current[1]}")
        lex.goNext()
        output+=lex.current_token_header()
        output+=opt_func_defs(lex)
        if lex.current[1] != "$":
            raise Exception(f"Error in rat24s - Expected $ separator but encountered {lex.current[1]}")
        lex.goNext()
        output+=lex.current_token_header()

        output+=opt_dec_list(lex)
        if lex.current[1] != "$":
            raise Exception(f"Error in rat24s - Expected $ separator but encountered {lex.current[1]}")
        lex.goNext()
        output+=lex.current_token_header()
        output+=statement_list(lex)
        if lex.current[1] != "$":   
            raise Exception(f"Error in rat24s - Expected $ separator but encountered {lex.current[1]}")
    except Exception as e:
        raise Exception(str(e))
    else: return output+"\n| ~~~        End of File Reached      ~~~ |\n| ~~~ Syntax Analyzer Found No Errors ~~~ |"
# <Opt Function Definitions> -> <Function Definitions>     |  <Empty>
def opt_func_defs(lex):
    try:
        output = "<Opt Function Definitions> -> <Function Definitions>\n"
        output += function_defs(lex)
        return output
    except:
        return "<Opt Function Definitions> -> <Empty>\n"+empty(lex)

# <Opt Declaration List> -> <Declaration List> | <Empty>
def opt_dec_list(lex):
    try:
        output = "<Opt Declaration List> -> <Declaration List>\n"
        output+= declaration_list(lex)
        return output
    except:
        output= "<Opt Declaration List> -> <Empty>\n"
        output+= empty(lex)
        return output

# <Body> -> {<Statement List>}
def body(lex):
    if lex.current[1]!="{":
        raise Exception("Error in body() - Expected {")
    lex.goNext()
    output = lex.current_token_header()
    output += "<Body> -> {<Statement List>}\n"
    output+=statement_list(lex)
    if lex.current[1]!="}":
        raise Exception("Error in body() - Expected }")
    lex.goNext()
    output += lex.current_token_header()
    return output

# <Function Definitions> -> <Function><Function Definition Prime>
def function_defs(lex):
    output = "<Function Definitions> -> <Function> <Function Definition Prime>\n"
    output+= function_rule(lex)
    output += function_definition_prime(lex)
    return output

# <Function Definitions Prime> -> Epsilon | <Function Definitions>
def function_definition_prime(lex):
    try:
        output = "<Function Definitions Prime> -> <Function Definitions>\n"
        output += function_defs(lex)
        return output
    except:
        return "<Function Definitions Prime> -> Epsilon\n"

# <Function> -> function <Identifier> (<Opt Parameter List>) <Opt Declaration List> <Body>
def function_rule(lex):
    output = "<Function> -> function <Identifier> (<Opt Parameter List>) <Opt Declaration List> <Body>\n"
    if lex.current[1] != 'function':
        raise Exception("Error in function_rule() - Expected function keyword")
    lex.goNext()
    output += lex.current_token_header()
    if lex.current[0] != 'Identifier':
        raise Exception("Error in function_rule() - Expected function identifier")
    lex.goNext()
    output += lex.current_token_header()
    if lex.current[1] != '(':
        raise Exception("Error in function_rule()")
    lex.goNext()
    output+=lex.current_token_header()
    
    output+=opt_parameter_list(lex)
    
    if lex.current[1] != ')':
        raise Exception("Error in function_rule()")
    lex.goNext()
    output+=lex.current_token_header()
    output+=opt_dec_list(lex)
    
    output+=body(lex)
    
    return output

# <Opt Parameter List> -> <Parameter List> | <Empty>
def opt_parameter_list(lex):
    try:
        output = "<Opt Parameter List> -> <Parameter List> \n"
        output += parameter_list(lex)
        return output
    except:
        return "<Opt Parameter List> -> Empty\n"+empty(lex)
# <Parameter List> -> <Parameter> <Parameter List Prime>
def parameter_list(lex):
    output = "<Parameter List> -> <Parameter> <Parameter List Prime>\n"
    output+= parameter(lex)
    output+= parameter_list_prime(lex)
    return output

# <Parameter List Prime> -> Epsilon | ,<Parameter List>
def parameter_list_prime(lex):
    try:
        output = "<Parameter List Prime> ->,<Parameter List>\n"    
        if lex.current[1] != ',':
            raise Exception("Error in parameter_list_prime()")
        lex.goNext()
        output+=lex.current_token_header()
        output+=parameter_list(lex)
        return output
    except:
        return "<Parameter List Prime> -> Epsilon \n"    

# <Parameter> -> <IDs><Qualifier>
def parameter(lex):
    output="<Parameter> -> <IDs><Qualifier>\n"
    output+=ids(lex)
    output+=qualifier(lex)
    return output

# <Qualifier> -> integer | boolean | real
def qualifier(lex):
    if lex.current[1] in {"integer","boolean","real"}:
        output= f"<Qualifier> -> {lex.current[1]}\n"
        lex.goNext()
        output += lex.current_token_header()
        return output
    else: raise Exception("Error in qualifier()")

# <Declaration List> -> <Declaration>; <Declaration List Prime>
def declaration_list(lex):
    output = declaration(lex)
    if lex.current[1]!=';':
        raise Exception("Error in declaration_list()")
    lex.goNext()
    output+=lex.current_token_header()
    output+=declaration_list_prime(lex)
    return output

# <Declaration List Prime> -> Epsilon | <Declaration List>
def declaration_list_prime(lex):
    try:
        output="<Declaration List Prime> -> <Declaration List>\n"
        output+=declaration_list(lex)
        return output
    except:
        return"<Declaration List Prime> -> Epsilon\n"
    
# <Declaration> -> <Qualifier><IDs>
def declaration(lex):
    output="<Declaration> -> <Qualifier><IDs>\n"
    output+=qualifier(lex)
    output+=ids(lex)
    return output

# <IDs> -> <Identifier> <IDs Prime>
def ids(lex):
    output="<IDs> -> <Identifier> <IDs Prime>\n"
    if lex.current[0] != "Identifier":
        raise Exception("Error in ids()")
    lex.goNext()
    output+=lex.current_token_header()
    output+=ids_prime(lex)
    return output

# <IDs Prime> -> Epsilon | ,<IDs>
def ids_prime(lex):
    try:
        output="<IDs Prime> -> <IDs>\n"
        if lex.current [1] != ',':
            raise Exception("Error in ids_prime()")
        lex.goNext()
        output+=lex.current_token_header()
        output+=ids(lex)
        return output
    except:
        return "<IDs Prime> -> Epsilon\n"

# <Statement List> -> <Statement> <Statement List Prime>
def statement_list(lex):
    output = "<Statement List> -> <Statement><Statement List Prime>\n"

    output += statement(lex)
    output += statement_list_prime(lex)
    return output

# Statment List Prime -> <Statement List> | <Empty>
def statement_list_prime(lex):
    output=""
    try:
        output+="<Statement List Prime> -> <Statement List>\n"
        output+=statement_list(lex)
        return output
    except:
        return "<Statement List Prime> -> <Empty>\n"+empty(lex)

# <Statement> ->   <Compound>  |  <Assign>  |   <If>  |  <Return>   | <Print>   |   <Scan>   |  <While>
def statement(lex):
    output = ""
    try:
        output="<Statement> -> <Assign>\n"
        output+=assign(lex)
        return output
    except Exception as e:
        pass
    try:
        output="<Statement> -> <Scan>\n"
        output+=scan(lex)
        return output
    except Exception as e:
        pass
    try:
        output="<Statement> -> <While>\n"
        output+=while_rule(lex)
        return output
    except Exception as e:
        pass
    try:
        output="<Statement> -> <Return>\n"
        output+=return_rule(lex)
        return output
    except Exception as e:
        pass
    try:
        output="<Statement> -> <If>\n"
        output+=if_rule(lex)
        return output
    except Exception as e:
        pass
    try:
        output="<Compound>> -> <Compound>\n"
        output+=compound(lex)
        return output
    except Exception as e:
        pass
    try:
        output="<Statement> -> <Print>\n"
        output+=print_rule(lex)
        return output
    except Exception as e:
        raise Exception("Error in statement -> Expected <Compound>  |  <Assign>  |   <If>  |  <Return>   | <Print>   |   <Scan>   |  <While>\n")

# <Compound> -> { <Statement List> }
def compound(lex):
    # same as body()
    output="<Compound> -> {<Statement List>}\n"
    return output+body(lex)

# <Print> -> print ( <Expression>);
def print_rule(lex):
    if lex.current[1] != "print":
        raise Exception("Error in print() - expected print keyword")
    else:
        output = "<Print> -> print(<Expression>)\n"
        lex.goNext()
        output += lex.current_token_header()
        if lex.current[1] != "(":
            raise Exception("Error in print()")
        lex.goNext()
        output += lex.current_token_header()
        output+=expression(lex)
        if lex.current[1] != ")":
            raise Exception("Error in print()")
        lex.goNext()
        output += lex.current_token_header()
        if lex.current[1] != ";":
            raise Exception("Error in print()")
        lex.goNext()
        output += lex.current_token_header()
        return output

# Assign -> <Identifier> = <Expression>;
def assign(lex):
    output = ""
    if lex.getCurrent()[0] == "Identifier":
        # TODO SAVE TOKEN HERE (SAVE ID ID=....)
        save = lex.getCurrent()
        output += "<Assign> -> Identifier = <Expression>;\n"
        lex.goNext()
        if lex.current[1] != "=":
            raise Exception("Error in assign()")
        output += lex.current_token_header()
        lex.goNext()
        output += lex.current_token_header()
        output += expression(lex)
        # TODO GENERATE INSTURUCTION HERE
        dict[save[1]] = mem_address 
        print(dict[save[1]])

        generate_instruction("POPM",get_Address(save[1]))
        print("xxx")
        if lex.current[1] != ";":
            raise Exception("Error in assign()")
        lex.goNext()
        output += lex.current_token_header()
        return output
    else: raise Exception("Error in assign() - Expected <Identifier>")

# Expression = Term  Expression'
def expression(lex):
    output = "<Expression> -> <Term><Expression Prime>\n"
    
    output += term(lex)
    
    output += expresssion_prime(lex)
    
    return output

# Expression' = +Term  Expression' | -Term  Expression' | Epsilon
def expresssion_prime(lex):
    output = ""
    if lex.getCurrent()[1] in {"-", "+"}:
        if lex.getCurrent()[1] == "-":
            output += "<Expression Prime> -> - <Term><Expression Prime>\n"
        else:
            output += "<Expression Prime> -> + <Term><Expression Prime>\n"
        lex.goNext()
        output += lex.current_token_header()
        output += term(lex)
        # TODO
        generate_instruction("A","nil")
        output += expresssion_prime(lex)
        return output
    else:
        output += "<Expression Prime> -> Epsilon\n"
        return output

# Term = Factor Term'
def term(lex):
    output = "<Term> -> <Factor><Term Prime>\n"
    
    output += factor(lex)
    
    output += term_prime(lex)
    return output

# Term' = *Factor  Term'   |   /Factor  Term'   |   Epsilon
def term_prime(lex):
    output = ""
    if lex.getCurrent()[1] in {"*", "/"}:
        if lex.getCurrent()[1] == "/":
            output += "<Term Prime> -> /<Factor><Term Prime>\n"
        else:
            output += "<Term Prime> -> *<Factor><Term Prime>\n"
        lex.goNext()
        output += lex.current_token_header()
        output += factor(lex)
        generate_instruction("A","nil")
        output += term_prime(lex)
        return output
    else:
        output += "<Term Prime> -> Epsilon\n"
        return output

# <Factor> -> -<Primary> | <Primary>
def factor(lex):
    current = lex.current
    try:
        if current[1] == "-":
            output = "<Factor> -> -<Primary>\n"
            lex.goNext()
            output+=lex.current_token_header()
            output+=primary(lex)

            return output
        else: raise Exception()
    except:
        pass
    try:
        output = "<Factor> -> <Primary>\n"
        output += primary(lex)
        return output
    except:
        raise Exception( "Error in factor() - Expected -<Primary> | <Primary>\n")

# <Primary> -> <Identifier> | <Integer> | <Real> | true | false ........
def primary(lex):
    current = lex.current
    
    try:
        if current[0] in {"Integer","Real"}:
            output = f"<Primary> -> <{current[0]}>\n"
            global mem_address
            generate_instruction("PUSHM",mem_address)
            mem_address+=1
        elif current[1] in {"true","false"}:
            output = f"<Primary> -> <{current[1]}>\n"
        else: raise Exception("Not Integer | Real | true | false")
        lex.goNext()
        output+=lex.current_token_header()
        return output
    except Exception as e:
        # print(e)
        pass

    try:
        if current[0] in {"Identifier"}:
          
            output="<Primary> -> <Identifier>(<IDs>)\n"
            output+=lex.goNext()
     
            if lex.current[1] != "(":
                lex.goBack(1)
                raise Exception("Error - Expected (")
            output+=lex.goNext()
            output+=ids(lex)
            if lex.current[1] != ")":
                raise Exception("Error - Expected )")
            lex.goNext()
            return output

        else: raise Exception("Identifier or <Identifier>(<IDs>)")
    except Exception as e:
        # print(e)
        pass
    
    try:
        if current[0] in {"Identifier"}:
            
            output = f"<Primary> -> <Identifier>\n"
            # TODO
            generate_instruction("PUSHM",get_Address(current[1]))
            lex.goNext()
            output+=lex.current_token_header()
            
            return output
        else: raise Exception("ERROR")
    except:
        pass
    
    try:
        if current[1] == "(":
            output = f"<Primary> -> (<Expression>)\n"
            lex.goNext()
            output+=lex.current_token_header()
            output+=expression(lex)
            if lex.current[1]!=")":
                raise Exception("Expected )")
            lex.goNext()

            output+=lex.current_token_header()
            return output
        else: raise Exception("Expected (")
    except Exception as e:
        # print(e)
        pass
    raise Exception ("Error in primary() - Expected  <Identifier> | <Integer>  |  <Identifier>  ( <IDs> ) | ( <Expression> ) | <Real>  | true | false\n ")

# <Scan> -> scan ( <IDs> );
def scan(lex):
    if lex.current[1] != "scan":
        raise Exception("Error in scan() - Expected 'scan' keyword")
    else:
        output = "<Scan> -> scan(<IDs>);\n"
        lex.goNext()
        output += lex.current_token_header()
        if lex.current[1] != "(":
            raise Exception("Error in scan() - Expected '(' after 'scan'")
        lex.goNext()
        output += lex.current_token_header()
        output += ids(lex)
        if lex.current[1] != ")":
            raise Exception("Error in scan() - Expected ')' after identifier")
        lex.goNext()
        output += lex.current_token_header()
        if lex.current[1] != ";":
            raise Exception("Error in scan() - Expected ';' after scan statement")
        lex.goNext()
        output += lex.current_token_header()
        return output
    
# <Empty> -> Epsilon
def empty(lex):
    return "<Empty> -> Epsilon\n"

# <Relop> ->  ==  |  !=   |   >   |  <  |  <=  |   =>
def relop(lex):
    output = ""
    try:
        operator = lex.current[1]
        if operator in {"==", "<=", "=>", "<", ">", "!="}:
            output = "<Relop> -> " + operator + "\n"
            lex.goNext()
            output += lex.current_token_header()
            return output
        else:
            raise Exception("Error in relop() - Invalid relational operator")
    except Exception as e:
        raise Exception("Error in relop() - " + str(e))

# <Return> -> return <Return Prime>
def return_rule(lex):
    output="<Return> -> return <Return Prime>\n"
    if lex.current[1] != "return":
        raise Exception("Error in return() - Expected return keyword")
    lex.goNext()
    output+=lex.current_token_header()
    output+=return_prime(lex)
    return output

# <Return Prime> ->  ; |  <Expression> ;
def return_prime(lex):
    output="<Return Prime> ->  ; |  <Expression>;\n"
    try:
        if lex.current[1] == ";":
            output+= "<Return Prime> -> ;\n"
            lex.goNext()
            output+=lex.current_token_header()
            return output
        else:
            raise Exception("")
    except:
        pass
    try:
        output+=expression(lex)
        if lex.current[1] != ";":
            raise Exception("Error in return_prime() - Expected ;\n")
        lex.goNext()
        output+=lex.current_token_header()
        return output
    except:
        if lex.current[1] != ";":
            raise Exception("Error in return_prime() - Expected ;")
        return "<Return Prime> -> ;\n"

# <While> -> while ( <Condition>  )  <Statement>  endwhile
def while_rule(lex):
    output="<While> -> while ( <Condition>  )  <Statement>  endwhile"
    if lex.current[1] != "while":
        raise Exception("Error in while() - Expected while keyword")
    output+=lex.goNext()
    if lex.current[1] != "(":
        raise Exception("Error in while() - (")
    output+=lex.goNext()
    output+=condition(lex)
    if lex.current[1] != ")":
        raise Exception("Error in while() - )")
    output+=lex.goNext()
    output+=statement(lex)
    if lex.current[1] != "endwhile":
        raise Exception("Error in while() - Expected endwhile keyword")
    output+=lex.goNext()
    return output

# <Condition> -> <Expression> <Relop> <Expression>
def condition(lex):
    output="<Condition> -> <Expression> <Relop> <Expression>\n"
    
    output+=expression(lex)
    
    output+=relop(lex)
    
    output+=expression(lex)
    
    return output
# <If> -> if  ( <Condition>  ) <Statement>    <If Prime>
def if_rule(lex):
    output = "<If> -> if (<Condition>) <Statement> <If Prime>\n"
    
    if lex.current[1] != "if":
        raise Exception("Error in if_rule() - Expected 'if' keyword")
    lex.goNext()
    output += lex.current_token_header()
    if lex.current[1] != "(":
        raise Exception("Error in if_rule() - Expected '(' after 'if'")
    
    lex.goNext()
    output += lex.current_token_header()
    
    output += condition(lex)
    

    if lex.current[1] != ")":
        raise Exception("Error in if_rule() - Expected ')' after condition")
    lex.goNext()
    output += lex.current_token_header()
    output += statement(lex)
    output += if_prime(lex)
    return output

# <If Prime> -> endif | else <Statement> endif
def if_prime(lex):
    output = ""
    try:
        if lex.current[1] != "else":
            raise Exception("Error in if_prime() -> Expected an 'else'")
        output += "<If'> -> else <Statement> endif\n"
        lex.goNext()
        output += lex.current_token_header()
        output += statement(lex)
        if lex.current[1] != "endif":
            raise Exception("Error in if_prime() -> Expected an 'endif'")
        output += lex.goNext()
        return output
    except:
        output += "<If Prime> -> endif\n"
        output+=lex.goNext()
        return output
# DIVIDER

def syntax_analyzer(input_file,output_file):

    # For Testing Individual Functions
    try:
        lexer=Lexer(lexical_analyzer(input_file))
        output = rat24s(lexer)
        print(output)
        with open(output_file, 'w') as file:
            file.write(output)
            file.close()
        global inst
        print(inst)
        for x in inst:
            if x:
                print(f'{x[0]} {x[1]} {x[2]}')
            else:
                print('-')
    except Exception as e:
        print(e)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Error =====\nUsage: python3 assignemnt2.py <input_file> <output_file>")
        sys.exit(1)
    input_file, output_file = sys.argv[1], sys.argv[2]

    syntax_analyzer(input_file,output_file)
