from src.lexer.token import Token

# kelas ParseTree merepresentasikan node dalam pohon parse
class ParseTree: 
    def __init__(self, value, children=None):
        self.value = value # string or Token for leaves
        self.children = children if children is not None else []

        self.line = None
        self.col = None

        if isinstance(value, Token):
            self.line = value.line
            self.col = value.col

        # if no position yet, try to inherit from first child that has one
        for child in self.children:
            if isinstance(child, ParseTree) and child.line is not None:
                if self.line is None:
                    self.line = child.line
                    self.col = child.col
                    break

    def add_child(self, child):
        self.children.append(child)

        if self.line is None and isinstance(child, ParseTree) and child.line is not None:
            self.line = child.line
            self.col = child.col


    def is_leaf(self):
        return len(self.children) == 0

    def __repr__(self):
        return f"ParseTree({self.value!r}, children={self.children!r}, pos={self.line}:{self.col})"


    def pretty_print(self, prefix="", is_last=True):
        """
        prefix: indent sebelum node
        is_last: apakah node ini anak terakhir
        """

        branch = "└── " if is_last else "├── "

        if isinstance(self.value, Token):
            node_label = repr(self.value)
        else:
            node_label = str(self.value)

        print(prefix + branch + node_label)

        if is_last:
            new_prefix = prefix + "    "
        else:
            new_prefix = prefix + "│   "

        for i, child in enumerate(self.children):
            child.pretty_print(new_prefix, i == len(self.children) - 1)
