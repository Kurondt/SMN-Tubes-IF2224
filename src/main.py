from .cli import parse_args
# from .lexer.rules_loader import DFARules
# from .lexer.scanner import Scanner
from .errors import LexError
from src.lexer.rules_loader import Rule
from src.lexer.scanner import Scanner

def main():
    args = parse_args()

    text = args.source.read_text(encoding="utf-8")
    rules = Rule().load_rule(args.dfa)
    scanner = Scanner(rules, text)
    try:
        for tok in scanner.tokenize():
            print(repr(tok))
    except LexError as e:
        print(e)

if __name__ == "__main__":
    main()

