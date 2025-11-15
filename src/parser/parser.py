

from src.parser.parsertree import ParseTree
from src.lexer.token import Token
from src.errors import SyntaxError

class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def lookahead(self) -> Token:
        return self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None

    def next_token(self):
        self.pos += 1

    def parse(self) -> ParseTree:
        pass 

    def match(self, token_type : str, token_value: str = None) -> bool:
        if self.peek().type == token_type and (token_value is None or self.peek().value == token_value):
            return True
        return False

    def consume(self, token_type : str, token_value: str = None) -> ParseTree:
        token = self.peek()
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
            node.add_child(self.consume("DOT"))
        return node

    def program_header(self) :
        node = ParseTree("<program_header>")
        if self.match("KEYWORD", "program"):
            node.add_child(self.consume("KEYWORD", "program"))
        if self.match("IDENTIFIER"):
            node.add_child(self.consume("IDENTIFIER"))
        if self.match("SEMICOLON"):
            node.add_child(self.consume("SEMICOLON"))

        return node

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


    def const_declaration(self) -> ParseTree:
        node = ParseTree("<const_declaration>")
        if self.match("KEYWORD", "konstanta"):
            node.add_child(self.consume("KEYWORD", "konstanta"))

        if not self.match("IDENTIFIER"):
            raise SyntaxError("Expected identifier in constant declaration", self.peek().line, self.peek().col)
        
        while self.match("IDENTIFIER"):
            node.add_child(self.consume("IDENTIFIER"))
            if self.match("ASSIGN_OPERATOR"):
                node.add_child(self.consume("ASSIGN_OPERATOR"))
            if self.match("NUMBER") or self.match("STRING_LITERAL") or self.match("CHAR_LITERAL"):
                node.add_child(self.consume(self.peek().type))
            if self.match("SEMICOLON"):
                node.add_child(self.consume("SEMICOLON"))

        return node
            
    def type_declaration(self) -> ParseTree:
        node = ParseTree("<type_declaration>")
        if self.match("KEYWORD", "tipe"):
            node.add_child(self.consume("KEYWORD", "tipe"))

        if not self.match("IDENTIFIER"):
            raise SyntaxError("Expected identifier in type declaration", self.peek().line, self.peek().col)
        
        while self.match("IDENTIFIER"):
            node.add_child(self.consume("IDENTIFIER"))
            if self.match("ASSIGN_OPERATOR"):
                node.add_child(self.consume("ASSIGN_OPERATOR"))
            node.add_child(self.type())
            # TODO : handle type definition 
            if self.match("SEMICOLON"):
                node.add_child(self.consume("SEMICOLON"))

    def var_declaration(self) -> ParseTree:
        node = ParseTree("<var_declaration>")
        if self.match("KEYWORD", "variabel"):
            node.add_child(self.consume("KEYWORD", "variabel"))
        
        node.add_child(self.identifier_list())

        if self.match("COLON"):
            node.add_child(self.consume("COLON"))

        node.add_child(self.type())

        if self.match("SEMICOLON"):
            node.add_child(self.consume("SEMICOLON"))

        return node

    def identifier_list(self) -> ParseTree:
        node = ParseTree("<identifier_list>")

        if self.match("IDENTIFIER"):
            node.add_child(self.consume("IDENTIFIER"))
        
        while self.match("COMMA"):
            node.add_child(self.consume("COMMA"))
            if self.match("IDENTIFIER"):
                node.add_child(self.consume("IDENTIFIER"))

    def type(self) -> ParseTree:
        pass

    def array_type(self) -> ParseTree:
        pass

    def range(self) -> ParseTree:
        pass

    def subprogram_declaration(self) -> ParseTree:
        node = ParseTree("<subprogram_declaration>")
        if self.match("KEYWORD", "prosedur"):
            node.add_child(self.procedure_declaration())
        elif self.match("KEYWORD", "fungsi"):
            node.add_child(self.function_declaration())
        return node

    def procedure_declaration(self) -> ParseTree:
        node = ParseTree("<procedure_declaration>")
        if self.match("KEYWORD", "prosedur"):
            node.add_child(self.consume("KEYWORD", "prosedur"))
        
        if self.match("LPARENTHESIS"):
            node.add_child(self.formal_parameter_list())
        
        if self.match("SEMICOLON"):
            node.add_child(self.consume("SEMICOLON"))

        # Handle block 

        if self.match("SEMICOLON"):
            node.add_child(self.consume("SEMICOLON"))

        return node

        
    def function_declaration(self) -> ParseTree:
        node = ParseTree("<function_declaration>")
        if self.match("KEYWORD", "fungsi"):
            node.add_child(self.consume("KEYWORD", "fungsi"))
        
        if self.match("LPARENTHESIS"):
            node.add_child(self.formal_parameter_list())
        
        if self.match("SEMICOLON"):
            node.add_child(self.consume("SEMICOLON"))

        # Handle block 

        if self.match("SEMICOLON"):
            node.add_child(self.consume("SEMICOLON"))

        return node

    def formal_parameter_list(self) -> ParseTree:
        node = ParseTree("<formal_parameter_list>")
        if self.match("LPARENTHESIS"):
            node.add_child(self.consume("LPARENTHESIS"))
        
        # Handle parameters group 

        while self.match("SEMICOLON"):
            node.add_child(self.consume("SEMICOLON"))

            # Handle parameters group

        if self.match("RPARENTHESIS"):
            node.add_child(self.consume("RPARENTHESIS"))

        return node

    def compound_statement(self) -> ParseTree :
        node = ParseTree("<compound_statement>")
        if self.match("KEYWORD", "mulai"):
            node.add_child(self.consume("KEYWORD", "mulai"))

        node.add_child(self.statement_list())

        if self.match("KEYWORD", "selesai"):
            node.add_child(self.consume("KEYWORD", "selesai"))