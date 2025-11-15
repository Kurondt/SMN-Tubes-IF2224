"""
Apa:
- panggil charstream, pake rules yang udah diload, jalanin dfa, ubah ke bentuk token

Ngapain:
- jalanin DFA per-karakter, ikutin rules
- setiap final state, map hasilnya ke bentuk token
- match symbol/token, kalo masi belum tentu, cek lookup table buat ngecek apakah hasilnya preserved word
- kalau invalid, misal ga ada transition untuk suatu karakter di state tertentu, raise/yield lexical error, sama keterangan yang jelas (line, col atau tambah deskripsi)

"""


from src.lexer.charstream import CharStream
from src.lexer.token import Token
from src.lexer.rules_loader import Rule
from src.errors import LexError
import re

class Scanner:
    def __init__(self, rules: Rule, filepath: str):
        self.cm: CharStream = CharStream(filepath)
        self.rules:Rule = Rule()
        self.rules = rules
        self.mapping: dict[str,str] = self.expand_char(self.rules.char_classes)

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []

        while True:
            token = self.next_token()
            if token is None:
                break
            tokens.append(token)

        return tokens

    def next_token(self) -> Token | None:
        self.skip_whitespace()

        cm = self.cm
        rules = self.rules

        if cm.eof():
            return None
        
        token_line, token_col = cm.get_pos()
        state = rules.initial_state
        last_acc_state = None
        last_acc_pos: tuple[int, int] | None = None
        last_acc_index: int | None = None
        last_acc_lexeme = ""
        lexeme = ""

        while not cm.eof():
            ch = cm.peek()
            char_class = self.classify_char(ch)

            next_state = rules.transition.get(state, {}).get(char_class)
            if next_state is None:
                next_state = rules.transition.get(state, {}).get("ANY")

            if next_state is None:
                break

            lexeme += cm.next()
            state = next_state

            if state in rules.final_states:
                last_acc_state = state
                last_acc_pos = cm.get_pos()
                last_acc_index = cm.pos
                last_acc_lexeme = lexeme

        if last_acc_state is not None and last_acc_pos is not None and last_acc_index is not None:
            cm.pos = last_acc_index
            cm.row, cm.col = last_acc_pos

            lexeme = last_acc_lexeme
            token_type = rules.final_states[last_acc_state]
            lookup_type = rules.lookup.get(lexeme.lower())
            if lookup_type is not None:
                token_type = lookup_type

            return Token(token_type, lexeme, token_line, token_col)
        
        error_char = cm.peek()
        err_line, err_col = cm.get_pos()
        raise LexError(f"Unexpected character '{error_char}' at {err_line}:{err_col}", err_line, err_col)

    def classify_char(self,ch: str) -> str:
        value = ""
        try:
            value = self.mapping[ch]
            if value == "ANY":
                return ch
            return value
        except KeyError:
            return ch
        except Exception as e:
            print(e)
            return ch
        
    def skip_whitespace(self):

        cm = self.cm
        
        while not cm.eof():
            ch = cm.peek()
            classes = self.classify_char(ch)
            if classes == "WHITESPACE":
                cm.next()
            else:
                break
                
    
    def expand_char(self, char_classes: dict[str, str],
                                code_range: tuple[int,int]=(0, 127)) -> dict[str, str]:
        compiled = []
        for name, spec in char_classes.items():
            s = (spec or "").strip()
            if not (s.startswith("^") and s.endswith("$")):
                if re.fullmatch(r"[A-Za-z0-9_\-\[\]\\ \t\n]+", s):
                    s = f"^[{s}]$"
                else:
                    s = f"^{s}$"
            try:
                pat = re.compile(s)
            except re.error:
                pat = re.compile(r"^$")
            compiled.append((name, pat))

        mapping: dict[str,str] = {}
        start, end = code_range
        for code in range(start, end + 1):
            ch = chr(code)
            for name, pat in compiled:
                if pat.match(ch):
                    if ch not in mapping:
                        mapping[ch] = name
                    break

        return mapping

                

if __name__ == "__main__":
    test = Scanner("rules/dfa.json", "../test/milestone-1/example.pas")
    print(test.mapping)
