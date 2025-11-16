

from src.parser.parsertree import ParseTree
from src.lexer.token import Token
from src.errors import SyntaxError

class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> ParseTree:
        return self.program()

    def peek(self) -> Token:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def lookahead(self) -> Token:
        return self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None

    def next_token(self):
        self.pos += 1

    def match(self, token_type : str, token_value: str = None) -> bool:
        token = self.peek()
        if token and token.type == token_type and (token_value is None or token.value == token_value):
            return True
        return False

    def match_ahead(self, token_type : str, token_value: str = None) -> bool:
        token = self.lookahead()
        if token and token.type == token_type and (token_value is None or token.value == token_value):
            return True
        return False

    def consume(self, token_type : str, token_value: str = None) -> ParseTree:
        token = self.peek()
        if (self.match(token_type, token_value)):
            self.next_token()
            return ParseTree(str(token))

        expected_type = token_type
        expected_value = f"with value [{token_value}]" if token_value is not None else ""
        actual_type = token.type if token else "EOF"
        actual_value = f"with value [{token.value}]" if token and token.value is not None else ""
        # raise SyntaxError(f"Expected {expected_type} {expected_value}, but got {actual_type} {actual_value}", token.line if token else "EOF", token.col if token else "")

    '''
    HARDCODED PRODUCTION RULES  

    // YAYAT
    daftar node : 
    program 
    program_header
    declaration_part
    const_declaration
    type_declaration
    var_declaration
    identifier_list
    type_definition (tambahan)
    type
    array_type
    record_type (tambahan)
    range 
    subprogram_declaration
    procedure_declaration
    function_declaration
    formal_parameter_list
    parameter_group (tambahan)
    compound_statement
    block (tambahan)

    // BAMA 
    statement_list
    statement (tambahan)
    assignment_statement
    if_statement
    while_statement
    for_statement
    procedure_or_function_call
    parameter_list
    expression
    simple_expression
    term
    factor
    relational_operator
    additive_operator
    multiplicative_operator

    '''

    # program -> program_header + declaration_part + compound_statement + DOT
    def program(self) -> ParseTree : 
        node = ParseTree("<program>")

        node.add_child(self.program_header())
        node.add_child(self.declaration_part())
        node.add_child(self.compound_statement())
        node.add_child(self.consume("DOT"))

        return node

    # program_header -> KEYWORD(program) + IDENTIFIER + SEMICOLON
    def program_header(self) :
        node = ParseTree("<program_header>")

        node.add_child(self.consume("KEYWORD", "program"))
        node.add_child(self.consume("IDENTIFIER"))
        node.add_child(self.consume("SEMICOLON"))

        return node

    # declaration_part -> (const_declaration)* + (type_declaration)* + (var_declaration)* + (subprogram_declaration)*
    def declaration_part(self) -> ParseTree :
        node = ParseTree("<declaration_part>")
        while self.match("KEYWORD", "konstanta"):
            node.add_child(self.const_declaration())
        while self.match("KEYWORD", "tipe"):
            node.add_child(self.type_declaration())
        while self.match("KEYWORD", "variabel"):
            node.add_child(self.var_declaration())
        while self.match("KEYWORD", "prosedur") or self.match("KEYWORD", "fungsi"):
            node.add_child(self.subprogram_declaration())

        return node

    # const_declaration -> KEYWORD(konstanta) + (IDENTIFIER + RELATIONAL_OPERATOR(=) + (NUMBER | STRING_LITERAL | CHAR_LITERAL) + SEMICOLON)+
    def const_declaration(self) -> ParseTree:
        node = ParseTree("<const_declaration>")

        node.add_child(self.consume("KEYWORD", "konstanta"))

        if not self.match("IDENTIFIER"):  # minimal ada satu identifier
            raise SyntaxError("Expected atleast one const declaration in constant declaration", self.peek().line, self.peek().col)
        
        while self.match("IDENTIFIER"):
            node.add_child(self.consume("IDENTIFIER"))
            node.add_child(self.consume("RELATIONAL_OPERATOR", "="))
            node.add_child(self.consume(self.peek().type))
            node.add_child(self.consume("SEMICOLON"))

        return node

    # type_declaration -> KEYWORD(tipe) + (IDENTIFIER + (RELATIONAL_OPERATOR(=) + type_definition + SEMICOLON)+
    def type_declaration(self) -> ParseTree:
        node = ParseTree("<type_declaration>")

        node.add_child(self.consume("KEYWORD", "tipe"))

        if not self.match("IDENTIFIER"):
            raise SyntaxError("Expected at least one identifier at type declaration", self.peek().line, self.peek().col)
        
        while self.match("IDENTIFIER"):
            node.add_child(self.consume("IDENTIFIER"))
            node.add_child(self.consume("RELATIONAL_OPERATOR", "="))
            node.add_child(self.type_definition())
            node.add_child(self.consume("SEMICOLON"))

        return node

    # var_declaration -> KEYWORD(variabel) + (identifier_list + COLON + type + SEMICOLON)+
    def var_declaration(self) -> ParseTree:
        node = ParseTree("<var_declaration>")

        node.add_child(self.consume("KEYWORD", "variabel"))

        if not self.match("IDENTIFIER"):
            raise SyntaxError("Expected at least one identifier at variable declaration", self.peek().line, self.peek().col)
        
        while self.match("IDENTIFIER"):
            node.add_child(self.identifier_list())
            node.add_child(self.consume("COLON"))
            node.add_child(self.type())
            node.add_child(self.consume("SEMICOLON"))


        return node

    # identifier_list -> IDENTIFIER + (COMMA + IDENTIFIER)*
    def identifier_list(self) -> ParseTree:
        node = ParseTree("<identifier_list>")

        node.add_child(self.consume("IDENTIFIER"))

        while self.match("COMMA"):
            node.add_child(self.consume("COMMA"))
            node.add_child(self.consume("IDENTIFIER"))

        return node 

    # type_definition -> type | record_type
    def type_definition(self) -> ParseTree:
        node = ParseTree("<type_definition>")

        if self.match("KEYWORD", "larik") or self.match("KEYWORD", "integer") or self.match("KEYWORD", "char") or self.match("KEYWORD", "boolean") or self.match("KEYWORD", "Real"):
            node.add_child(self.type())
        elif self.match("KEYWORD", "rekaman"):
            node.add_child(self.record_type())

        return node

    # type -> array_type | KEYWORD(integer | char | boolean | Real)
    def type(self) -> ParseTree:
        node = ParseTree("<type>")
        
        if self.match("KEYWORD", "larik"):
            node.add_child(self.array_type())
        else :
            node.add_child(self.consume("KEYWORD"))

        return node

    # array_type -> KEYWORD(larik) + LBRACKET + range + RBRACKET + KEYWORD(dari) + type
    def array_type(self) -> ParseTree:
        node = ParseTree("<array_type>")

        node.add_child(self.consume("KEYWORD", "larik"))
        node.add_child(self.consume("LBRACKET"))
        node.add_child(self.range())
        node.add_child(self.consume("RBRACKET"))
        node.add_child(self.consume("KEYWORD", "dari"))
        node.add_child(self.type())

        return node

    # record_type -> KEYWORD(rekaman) + (identifier_list + COLON + type + SEMICOLON)+ + KEYWORD(selesai)
    def record_type(self) -> ParseTree:
        node = ParseTree("<record_type>")

        node.add_child(self.consume("KEYWORD", "rekaman"))

        if not self.match("IDENTIFIER"):
            raise SyntaxError("Expected at least one identifier at record definition , got " + str(self.peek().type) + str(self.peek().value), self.peek().line, self.peek().col)
        
        while self.match("IDENTIFIER"):
            node.add_child(self.identifier_list())
            node.add_child(self.consume("COLON"))
            node.add_child(self.type())
            node.add_child(self.consume("SEMICOLON"))

        node.add_child(self.consume("KEYWORD", "selesai"))

        return node

    # range -> expression + RANGE_OPERATOR(..) + expression
    def range(self) -> ParseTree:
        node = ParseTree("<range>")

        node.add_child(self.expression())
        node.add_child(self.consume("RANGE_OPERATOR", ".."))
        node.add_child(self.expression())

        return node

    # subprogram_declaration -> procedure_declaration | function_declaration
    def subprogram_declaration(self) -> ParseTree:
        node = ParseTree("<subprogram_declaration>")
        if self.match("KEYWORD", "prosedur"):
            node.add_child(self.procedure_declaration())
        elif self.match("KEYWORD", "fungsi"):
            node.add_child(self.function_declaration())

        return node

    # procedure_declaration -> KEYWORD(prosedur) + IDENTIFIER + (formal_parameter_list)? + SEMICOLON + block + SEMICOLON
    def procedure_declaration(self) -> ParseTree:
        node = ParseTree("<procedure_declaration>")
        
        node.add_child(self.consume("KEYWORD", "prosedur"))
        node.add_child(self.consume("IDENTIFIER"))

        if self.match("LPARENTHESIS"):
            node.add_child(self.formal_parameter_list())

        node.add_child(self.consume("SEMICOLON"))
        node.add_child(self.block())
        node.add_child(self.consume("SEMICOLON"))

        return node

    # function_declaration -> KEYWORD(fungsi) + IDENTIFIER + (formal_parameter_list)? + COLON + type + SEMICOLON + block + SEMICOLON
    def function_declaration(self) -> ParseTree:
        node = ParseTree("<function_declaration>")

        node.add_child(self.consume("KEYWORD", "fungsi"))
        node.add_child(self.consume("IDENTIFIER"))

        if self.match("LPARENTHESIS"):
            node.add_child(self.formal_parameter_list())

        node.add_child(self.consume("COLON"))
        node.add_child(self.type())
        node.add_child(self.consume("SEMICOLON"))
        node.add_child(self.block())
        node.add_child(self.consume("SEMICOLON"))


        return node

    # formal_parameter_list -> LPARENTHESIS + parameter_group + (SEMICOLON + parameter_group)* + RPARENTHESIS
    def formal_parameter_list(self) -> ParseTree:
        node = ParseTree("<formal_parameter_list>")

        node.add_child(self.consume("LPARENTHESIS"))

        node.add_child(self.parameter_group()) 

        while self.match("SEMICOLON"):
            node.add_child(self.consume("SEMICOLON"))

            node.add_child(self.parameter_group())

        node.add_child(self.consume("RPARENTHESIS"))

        return node

    # parameter_group -> identifier_list + COLON + type
    def parameter_group(self) -> ParseTree:
        node = ParseTree("<parameter_group>")

        node.add_child(self.identifier_list())

        node.add_child(self.consume("COLON"))

        node.add_child(self.type())

        return node

    # compound_statement -> KEYWORD(mulai) + statement_list + KEYWORD(selesai)
    def compound_statement(self) -> ParseTree :
        node = ParseTree("<compound_statement>")

        node.add_child(self.consume("KEYWORD", "mulai"))

        node.add_child(self.statement_list())

        node.add_child(self.consume("KEYWORD", "selesai"))

        return node

    # block -> (declaration_part)? + compound_statement
    def block(self) -> ParseTree:
        node = ParseTree("<block>")

        if self.match("KEYWORD", "konstanta") or self.match("KEYWORD", "tipe") or self.match("KEYWORD", "variabel") or self.match("KEYWORD", "prosedur") or self.match("KEYWORD", "fungsi"):
            node.add_child(self.declaration_part())

        node.add_child(self.compound_statement())

        return node

    # statement_list -> statement + (SEMICOLON + statement)*
    def statement_list(self) -> ParseTree:
        node = ParseTree("<statement-list>")
        
        node.add_child(self.statement())
        
        while self.match("SEMICOLON", ";"):
            
            if self.lookahead() and self.lookahead().type == "KEYWORD" and self.lookahead().value == "selesai":
                node.add_child(self.consume("SEMICOLON", ";"))
                break

            node.add_child(self.consume("SEMICOLON", ";"))
            node.add_child(self.statement())
            
        return node

    # statement -> compound_statement | if_statement | while_statement | for_statement | assignment_statement | procedure_or_function_call
    def statement(self) -> ParseTree:
        node = ParseTree("<statement>")
        
        if self.match("KEYWORD", "mulai"):
            node.add_child(self.compound_statement())
            
        elif self.match("KEYWORD", "jika"):
            node.add_child(self.if_statement())
            
        elif self.match("KEYWORD", "selama"):
            node.add_child(self.while_statement())
            
        elif self.match("KEYWORD", "untuk"):
            node.add_child(self.for_statement())
            
        elif self.match("IDENTIFIER"):

            if self.lookahead() and self.lookahead().type == "ASSIGN_OPERATOR":
                node.add_child(self.assignment_statement())
            else:
                node.add_child(self.procedure_or_function_call())

        return node
        

    # assignment_statement -> IDENTIFIER + ASSIGN_OPERATOR(:=) + expression
    def assignment_statement(self):
        node = ParseTree("<assignment-statement>")
        
        node.add_child(self.consume("IDENTIFIER"))
        node.add_child(self.consume("ASSIGN_OPERATOR", ":="))
        node.add_child(self.expression())

        return node

    # if_statement -> KEYWORD(jika) + expression + KEYWORD(maka) + statement + (KEYWORD(selain_itu) + statement)?
    def if_statement(self):
        node = ParseTree("<if-statement>")

        node.add_child(self.consume("KEYWORD", "jika"))
        node.add_child(self.expression())
        node.add_child(self.consume("KEYWORD", "maka"))
        node.add_child(self.statement())

        if (self.match("KEYWORD", "selain_itu")):
            node.add_child(self.consume("KEYWORD", "selain_itu"))
            node.add_child(self.statement())

        return node

    # while_statement -> KEYWORD(selama) + expression + KEYWORD(lakukan) + statement
    def while_statement(self):
        node = ParseTree("<while-statement>")

        node.add_child(self.consume("KEYWORD", "selama"))
        node.add_child(self.expression())
        node.add_child(self.consume("KEYWORD", "lakukan"))
        node.add_child(self.statement())

        return node
    
    # for_statement -> KEYWORD(untuk) + IDENTIFIER + ASSIGN_OPERATOR(:=) + expression + (KEYWORD(ke) | KEYWORD(turun_ke)) + expression + KEYWORD(lakukan) + statement
    def for_statement(self):
        node = ParseTree("<for-statement>")

        node.add_child(self.consume("KEYWORD", "untuk"))
        node.add_child(self.consume("IDENTIFIER"))
        node.add_child(self.consume("ASSIGN_OPERATOR", ":="))
        node.add_child(self.expression())

        if (self.match("KEYWORD", "ke")):
            node.add_child(self.consume("KEYWORD", "ke"))
        else:
            node.add_child(self.consume("KEYWORD", "turun_ke"))

        node.add_child(self.expression())
        node.add_child(self.consume("KEYWORD", "lakukan"))
        node.add_child(self.statement())

        return node
    
    # procedure_or_function_call -> IDENTIFIER + LPARENTHESIS + (parameter_list)? + RPARENTHESIS
    def procedure_or_function_call(self):
        node = ParseTree("<procedure/function-call>")

        node.add_child(self.consume("IDENTIFIER"))
        node.add_child(self.consume("LPARENTHESIS", "("))

        if (not self.match("RPARENTHESIS", ")")):
            node.add_child(self.parameter_list())

        node.add_child(self.consume("RPARENTHESIS", ")"))

        return node

    # parameter_list -> (expression | string_literal | char_literal) + (COMMA + (expression | string_literal | char_literal))*
    def parameter_list(self):
        node = ParseTree("<parameter-list>")

        if self.match("STRING_LITERAL"):
            node.add_child(self.consume("STRING_LITERAL"))
        elif self.match("CHAR_LITERAL"):
            node.add_child(self.consume("CHAR_LITERAL"))
        else:
            node.add_child(self.expression())

        while self.match("COMMA", ","):
            node.add_child(self.consume("COMMA", ","))
            node.add_child(self.expression())

        return node

    # expression -> simple_expression + (relational_operator + simple_expression)?
    def expression(self):
        node = ParseTree("<expression>")

        node.add_child(self.simple_expression())

        if self.match("RELATIONAL_OPERATOR"):
            node.add_child(self.relational_operator())
            node.add_child(self.simple_expression())

        return node

    # simple_expression -> (ARITHMETIC_OPERATOR(+ | -))? + term + (additive_operator + term)*
    def simple_expression(self):
        node = ParseTree("<simple-expression>")

        if self.match("ARITHMETIC_OPERATOR", "+"):
            node.add_child(self.consume("ARITHMETIC_OPERATOR", "+"))
        elif self.match("ARITHMETIC_OPERATOR", "-"):
            node.add_child(self.consume("ARITHMETIC_OPERATOR", "-"))
            
        node.add_child(self.term())

        while self.match("ARITHMETIC_OPERATOR", "+") or self.match("ARITHMETIC_OPERATOR", "-") or self.match("LOGICAL_OPERATOR", "atau"):
            node.add_child(self.additive_operator())
            node.add_child(self.term())

        return node

    # term -> factor + (multiplicative_operator + factor)*
    def term(self):
        node = ParseTree("<term>")

        node.add_child(self.factor())

        while self.match("ARITHMETIC_OPERATOR", "*") or self.match("ARITHMETIC_OPERATOR", "/") or self.match("LOGICAL_OPERATOR", "dan") or self.match("ARITHMETIC_OPERATOR", "mod") or self.match("ARITHMETIC_OPERATOR", "bagi"):
            node.add_child(self.multiplicative_operator())
            node.add_child(self.factor())

        return node

    # factor -> IDENTIFIER | NUMBER | CHAR_LITERAL | STRING_LITERAL | (LPARENTHESIS + expression + RPARENTHESIS) | LOGICAL_OPERATOR(tidak) + factor | function_call | KEYWORD(true | false)
    def factor(self):
        node = ParseTree("<factor>")

        if self.match("IDENTIFIER") and self.match_ahead("LPARENTHESIS", "("):
            node.add_child(self.procedure_or_function_call())
        elif self.match("IDENTIFIER"):
            node.add_child(self.consume("IDENTIFIER"))
        elif self.match("CHAR_LITERAL"):
            node.add_child(self.consume("CHAR_LITERAL"))
        elif self.match("STRING_LITERAL"):
            node.add_child(self.consume("STRING_LITERAL"))
        elif self.match("LPARENTHESIS", "("):
            node.add_child(self.consume("LPARENTHESIS", "("))
            node.add_child(self.expression())
            node.add_child(self.consume("RPARENTHESIS", ")"))
        elif self.match("LOGICAL_OPERATOR", "tidak"):
            node.add_child(self.consume("LOGICAL_OPERATOR", "tidak"))
            node.add_child(self.factor())
        elif self.match("KEYWORD", "true"):
            node.add_child(self.consume("KEYWORD", "true"))
        elif self.match("KEYWORD", "false"):
            node.add_child(self.consume("KEYWORD", "false"))
        else:
            node.add_child(self.consume("NUMBER"))

        return node
    
    # relational_operator -> RELATIONAL_OPERATOR(= | <> | < | <= | > | >=)
    def relational_operator(self):
        node = ParseTree("<relational-operator>")

        if self.match("RELATIONAL_OPERATOR", "="):
            node.add_child(self.consume("RELATIONAL_OPERATOR", "="))

        elif self.match("RELATIONAL_OPERATOR", "<>"):
            node.add_child(self.consume("RELATIONAL_OPERATOR", "<>"))

        elif self.match("RELATIONAL_OPERATOR", "<"):
            node.add_child(self.consume("RELATIONAL_OPERATOR", "<"))

        elif self.match("RELATIONAL_OPERATOR", "<="):
            node.add_child(self.consume("RELATIONAL_OPERATOR", "<="))

        elif self.match("RELATIONAL_OPERATOR", ">"):
            node.add_child(self.consume("RELATIONAL_OPERATOR", ">"))

        else:
            node.add_child(self.consume("RELATIONAL_OPERATOR", ">="))

        return node

    # additive_operator -> ARITHMETIC_OPERATOR(+ | -) | LOGICAL_OPERATOR(atau)
    def additive_operator(self):
        node = ParseTree("<additive-operator>")

        if self.match("ARITHMETIC_OPERATOR", "+"):
            node.add_child(self.consume("ARITHMETIC_OPERATOR", "+"))

        elif self.match("ARITHMETIC_OPERATOR", "-"):
            node.add_child(self.consume("ARITHMETIC_OPERATOR", "-"))

        else:
            node.add_child(self.consume("LOGICAL_OPERATOR", "atau"))

        return node
    
    # multiplicative_operator -> ARITHMETIC_OPERATOR(* | / | mod | bagi) | LOGICAL_OPERATOR(dan)
    def multiplicative_operator(self):
        node = ParseTree("<multiplicative-operator>")

        if self.match("ARITHMETIC_OPERATOR", "*"):
            node.add_child(self.consume("ARITHMETIC_OPERATOR", "*"))

        elif self.match("ARITHMETIC_OPERATOR", "/"):
            node.add_child(self.consume("ARITHMETIC_OPERATOR", "/"))

        elif self.match("ARITHMETIC_OPERATOR", "bagi"):
            node.add_child(self.consume("ARITHMETIC_OPERATOR", "bagi"))

        elif self.match("ARITHMETIC_OPERATOR", "mod"):
            node.add_child(self.consume("ARITHMETIC_OPERATOR", "mod"))

        else:
            node.add_child(self.consume("LOGICAL_OPERATOR", "dan"))

        return node

