"""
Apa:
- mesin karakter + tau posisi row/col

Ngapain:
- load text dari path
- peek (huruf apa saat ini), next (pindah huruf), eof (boolean, cek apakah sudah eof), current line/col ... kalau ada kebutuhan lain tambah aja
- track line/col

catatan:
- peek /next return '' aja pas EOF
"""

class CharStream:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.row = 1
        self.col = 1

    def eof(self) -> bool:
        return self.pos >= len(self.text)

    def peek(self) -> str: 
        if self.eof():
            return ''
        return self.text[self.pos]

    def next(self) -> str:
        # note : yg dilakukan next adalah (pindah posisi -> peek)
        char = self.peek()
        self.pos += 1
        if char == '\n':
            self.row += 1
            self.col = 1
        else :
            self.col += 1
        return char

    def get_pos(self) -> tuple[int, int]:
        return (self.row, self.col)
        
