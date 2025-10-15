from .cli import parse_args
# from .lexer.rules_loader import DFARules
# from .lexer.scanner import Scanner
from .errors import LexError

def main():
    args = parse_args()
    """
    # contoh kalau implementasi kelar
    text = args.source.read_text(encoding="utf-8")
    rules = DFARules.load(str(args.dfa))
    scanner = Scanner(rules, text)
    try:
        for tok in scanner.tokens():
            print(repr(tok))
    except LexError as e:
        print(e)
    """

if __name__ == "__main__":
    main()

