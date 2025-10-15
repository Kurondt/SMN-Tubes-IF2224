from dataclasses import dataclass

@dataclass(frozen=True)
class Token:
    type: str
    value: str
    line: int
    col: int

    def __repr__(self) -> str:
        return f"{self.type}({self.value})" if self.value != "" else f"{self.type}"
