

from src.parser.parsertree import ParseTree
from src.lexer.token import Token
from src.errors import SyntaxError

class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = 0

    def lookahead(self) -> Token:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def next_token(self):
        self.pos += 1

    def parse(self) -> ParseTree:
        pass 

    def match(self, token_type : str, token_value: str = None) -> bool:
        if self.lookahead().type == token_type and (token_value is None or self.lookahead().value == token_value):
            return True
        return False

    def consume(self, token_type : str, token_value: str = None) -> ParseTree:
        token = self.lookahead()
        if token.type == token_type and (token_value is None or token.value == token_value):
            self.next_token()
            return ParseTree(str(token))
        raise SyntaxError(f"Expected token {token_type} with value {token_value}, but got {token}", token.line, token.col)

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

    def program(self) -> ParseTree : 
        node = ParseTree("<program>")
        node.add_child(self.program_header())
        node.add_child(self.declaration_part())
        node.add_child(self.compound_statement())
        if self.match("DOT"):
            node.add_child(str(self.consume("DOT")))
        return node

    def program_header(self) :
        node = ParseTree("<program_header>")
        if self.match("KEYWORD", "program"):
            node.add_child(str(self.consume("KEYWORD", "program")))
        if self.match("IDENTIFIER"):
            node.add_child(str(self.consume("IDENTIFIER")))
        if self.match("SEMICOLON"):
            node.add_child(str(self.consume("SEMICOLON")))

        return node

    # def declaration_part(self) -> ParseTree :
    #     node = ParseTree("<declaration_part>")
    #     while self.match(

    def const_declaration(self) -> ParseTree:
        node = ParseTree("<const_declaration>")
        if self.match("KEYWORD", "konstanta"):
            node.add_child(str(self.consume("KEYWORD", "konstanta")))

        if not self.match("IDENTIFIER"):
            raise SyntaxError("Expected identifier in constant declaration", self.lookahead().line, self.lookahead().col)
        
        while self.match("IDENTIFIER"):
            node.add_child(str(self.consume("IDENTIFIER")))
            if self.match("ASSIGN_OPERATOR"):
                node.add_child(str(self.consume("ASSIGN_OPERATOR")))
            
            
        


