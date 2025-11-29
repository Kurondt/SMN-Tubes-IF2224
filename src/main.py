from .cli import parse_args
# from .lexer.rules_loader import DFARules
# from .lexer.scanner import Scanner
from .errors import LexError, SyntaxError, SemanticError
from src.lexer.rules_loader import Rule
from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.parser.parsertree import ParseTree
from src.semantic.analyzer import SemanticAnalyzer

def main():
    args = parse_args()

    text = args.source.read_text(encoding="utf-8")
    rules = Rule().load_rule(args.dfa)
    scanner = Scanner(rules, text)
    
    try:

        print("================== LEXYCAL ANALYSIS =================")
        token_list = scanner.tokenize()
        for tok in token_list:
            print(repr(tok))


        print("================== SYNTAX ANALYSIS =================")
        parser = Parser(token_list)
        parse_tree = parser.parse()
        parse_tree.pretty_print()

        print("================== SEMANTIC ANALYSIS =================")
        analyzer = SemanticAnalyzer()
        tab, btab, atab, ast = analyzer.analyze(parse_tree)
        
        analyzer.print_output(tab, btab, atab, ast)

    except LexError as e:
        print(e)
    except SyntaxError as e:
        print(e)
    except SemanticError as e:
        print(e)

if __name__ == "__main__":
    main()

