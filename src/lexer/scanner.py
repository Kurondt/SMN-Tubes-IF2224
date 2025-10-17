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
        tokens = []

        while True:
            token = self.next_token()
            if token is None:
                break
            elif token == "":
                pass
            tokens.append(token)

        return tokens

    def next_token(self) -> Token:

        self.skip_whitespace()

        cm = self.cm
        rules = self.rules

        if cm.eof():
            return None
        
        state = rules.initial_state
        last_acc_state = None
        last_acc_pos = None
        lexeme = ""

        while not cm.eof():
            ch = cm.peek()
            char_class = self.classify_char(ch)

            next_state = rules.transition.get(state, {}).get(char_class)

            if next_state is None:
                if rules.transition.get(state) is not None and rules.transition[state].get("ANY"):
                    next_state  = rules.transition[state]["ANY"]
                    pass
                else:
                    break

            lexeme += cm.next()
            state = next_state

            if state in rules.final_states:
                last_acc_state = state
                last_acc_pos = cm.get_pos()

        
        if last_acc_state: 
            token_type = rules.final_states[last_acc_state]
            # check loop table
            if rules.lookup.get(lexeme.lower()) is not None:
                token_type = rules.lookup.get(lexeme.lower())
            return Token(token_type, lexeme, last_acc_pos[0], last_acc_pos[1])
        
        raise LexError(f"Unexpected character '{cm.peek()}' at {cm.get_pos()}", cm.get_pos()[0], cm.get_pos()[1] - len(lexeme) + 1)

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
