

from src.parser.parsertree import ParserTree
from src.lexer.token import Token

class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = 0

    def lookahead(self) -> Token:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def parse(self) -> ParserTree:
        pass 

    def match(self, token_type : str, token_value: str = None) -> bool:
        if self.lookahead().type == token_type and (token_value is None or self.lookahead().value == token_value):
            self.pos += 1
            return True
        return False

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
    type
    array_type
    range 
    subprogram_declaration
    procedure_declaration
    function_declaration
    formal_parameter_list
    compound_statement

    // BAMA 
    statement_list
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

    def program(self) : 
        self.program_header()
        self.declaration_part()
        self.compound_statement()

        self.match("DOT")

    def program_header(self) :
        self.match("KEYWORD", "program")
        self.match("IDENTIFIER")
        self.match("SEMICOLON")

    def declaration_part(self) :


