

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
            if self.match("RELATIONAL_OPERATOR", "="):
                node.add_child(self.consume("RELATIONAL_OPERATOR", "="))
            if self.match("NUMBER") or self.match("STRING_LITERAL") or self.match("CHAR_LITERAL"):
                node.add_child(self.consume(self.peek().type))
            if self.match("SEMICOLON"):
                node.add_child(self.consume("SEMICOLON"))

        return node
            
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

    def statement(self) -> ParseTree:

        
        if self.match("KEYWORD", "mulai"):
            return self.compound_statement()
            
        elif self.match("KEYWORD", "jika"):
            return self.if_statement()
            
        elif self.match("KEYWORD", "selama"):
            return self.while_statement()
            
        elif self.match("KEYWORD", "untuk"):
            return self.for_statement()
            
        elif self.match("IDENTIFIER"):

            if self.lookahead() and self.lookahead().type == "ASSIGN_OPERATOR":
                return self.assignment_statement()
            else:
                return self.procedure_function_call()
        
        else:
            token = self.lookahead()

            raise SyntaxError(f"Expected a statement (mulai, jika, or IDENTIFIER), but got {token}",
                              token.line())

    def assignment_statement(self):
        node = ParseTree("<assignment-statement>")

        node.add_child(self.consume("IDENTIFIER"))
        node.add_child(self.consume("ASSIGN_OPERATOR"))
        node.add_child(self.expression())

        return node

    def if_statement(self):
        # TODO Coba koreksi, harusnya if ga wajib else
        node = ParseTree("<if-statement>")

        node.add_child(self.consume("KEYWORD", "jika"))
        node.add_child(self.expression())
        node.add_child(self.consume("KEYWORD", "maka"))
        node.add_child(self.statement())

        if (self.match("KEYWORD", "selain_itu")):
            node.add_child(self.consume("KEYWORD", "selain_itu"))
            node.add_child(self.statement())

        return node


    def while_statement(self):
        node = ParseTree("<while-statement>")

        node.add_child(self.consume("KEYWORD", "selama"))
        node.add_child(self.expression())
        node.add_child(self.consume("KEYWORD", "lakukan"))
        node.add_child(self.statement())

        return node
    
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
    
    def procedure_or_function_call(self):
        # TODO Harusnya sih ya , call tu ga wajib parameter list tapi di spek diwajibin ada, tapi aku implementasi ga wajib bodoamat wle
        node = ParseTree("<procedure/function-call>")

        node.add_child(self.consume("IDENTIFIER"))
        node.add_child(self.consume("LPARENTHESIS", "("))

        if (not self.match("RPARENTHESIS", ")")):
            node.add_child(self.parameter_list())

        node.add_child(self.consume("RPARENTHESIS", ")"))

        return node

    def parameter_list(self):
        node = ParseTree("<parameter-list>")

        node.add_child(self.expression())

        while self.match("COMMA", ","):
            node.add_child(self.consume("COMMA", ","))
            node.add_child(self.expression())

        return node

    def expression(self):
        node = ParseTree("<expression>")

        node.add_child(self.simple_expression())

        if self.match("RELATIONAL_OPERATOR"):
            node.add_child(self.relational_operator())
            node.add_child(self.simple_expression())

        return node

    def simple_expression(self):
        node = ParseTree("<simple-expression>")

        if self.match("ARITHMETIC_OPERATOR", "+"):
            node.add_child(self.consume("ARITHMETIC_OPERATOR", "+"))
        elif self.match("ARITHMETIC_OPERATOR", "-"):
            node.add_child(self.consume("ARITHMETIC_OPERATOR", "-"))
            
        node.add_child(self.term())

        while self.match("ARITHMETIC_OPERATOR", "+") or self.match("ARITHMETIC_OPERATOR", "-") or self.match("KEYWORD", "atau"):
            node.add_child(self.additive_operator())
            node.add_child(self.term())

        return node

    def term(self):
        node = ParseTree("<term>")

        node.add_child(self.factor())

        while self.match("ARITHMETIC_OPERATOR", "*") or self.match("ARITHMETIC_OPERATOR", "/") or self.match("KEYWORD", "dan") or self.match("ARITHMETIC_OPERATOR", "mod") or self.match("ARITHMETIC_OPERATOR", "bagi"):
            node.add_child(self.multiplicative_operator())
            node.add_child(self.term)

        return node

    def factor(self):
        node = ParseTree("<factor>")

        if self.match("IDENTIFIER"):
            node.add_child(self.consume("IDENTIFIER"))
        elif self.match("NUMBER"):
            node.add_child(self.consume("NUMBER"))
        elif self.match("CHAR_LITERAL", "'"):
            node.add_child(self.consume("CHAR_LITERAL", "'"))
        elif self.match("STRING_LITERAL", '"'):
            node.add_child(self.consume("STRING_LITERAL", '"'))
         # TODO ada masalah jadi ga dilanjutin dulu


        return node
    
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

    def additive_operator(self):
        node = ParseTree("<additive-operator>")

        if self.match("ARITHMETIC_OPERATOR", "+"):
            node.add_child(self.consume("ARITHMETIC_OPERATOR", "+"))

        elif self.match("ARITHMETIC_OPERATOR", "-"):
            node.add_child(self.consume("ARITHMETIC_OPERATOR", "-"))

        else:
            node.add_child(self.consume("KEYWORD", "atau"))

        return node
    
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
            node.add_child(self.consume("KEYWORD", "dan"))

        return node

    """
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
    """
       
    def type_declaration(self) -> ParseTree:
        node = ParseTree("<type_declaration>")
        if self.match("KEYWORD", "tipe"):
            node.add_child(self.consume("KEYWORD", "tipe"))

        if not self.match("IDENTIFIER"):
            raise SyntaxError("Expected identifier in type declaration", self.peek().line, self.peek().col)
        
        while self.match("IDENTIFIER"):
            node.add_child(self.consume("IDENTIFIER"))
            if self.match("RELATIONAL_OPERATOR", "="):
                node.add_child(self.consume("RELATIONAL_OPERATOR", "="))
            node.add_child(self.type())
            # TODO : handle type definition 
            if self.match("SEMICOLON"):
                node.add_child(self.consume("SEMICOLON"))

        return node

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

        return node 

    def type(self) -> ParseTree:
        node = ParseTree("<type>")
        
        if self.match("KEYWORD", "larik"):
            node.add_child(self.array_type())
        # elif self.match("KEYWORD", "rekaman"):
        #     node.add_child(self.record_type())
        elif self.match("KEYWORD", "integer") or self.match("KEYWORD", "char") or self.match("KEYWORD", "boolean") or self.match("KEYWORD", "Real"):
            node.add_child(self.consume("KEYWORD"))
        # else :
        #     raise SyntaxError(f"Expected type definition, we got {self.peek().type} {self.peek().value}", self.peek().line, self.peek().col)

        return node

    def array_type(self) -> ParseTree:
        node = ParseTree("<array_type>")
        return node

    def record_type(self) -> ParseTree:
        node = ParseTree("<record_type>")
        return node

    def range(self) -> ParseTree:
        node = ParseTree("<range>")
        return node

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

        return node