class LexError(Exception):
    def __init__(self, message: str, line: int, col: int):
        super().__init__(f"LexError at {line}:{col} – {message}")
        self.line = line
        self.col = col
        
class SyntaxError(Exception):
    def __init__(self, message: str, line: int, col: int):
        super().__init__(f"SyntaxError at {line}:{col} – {message}")
        self.line = line
        self.col = col

