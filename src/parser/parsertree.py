

class ParseTree: 
    def __init__(self, value, children=None):
        self.value = value
        self.children = children if children is not None else []

    def add_child(self, child):
        self.children.append(child)

    def is_leaf(self):
        return len(self.children) == 0

    def __repr__(self):
        return f"ParseTree({self.value!r}, children={self.children!r})"
    
    def pretty_print(self, indent=0):
        print(' ' * indent + str(self.value))
        for child in self.children:
            child.pretty_print(indent + 1)

    def pretty_print_2(self, prefix="", is_last=True):
        """
        prefix: indent sebelum node
        is_last: apakah node ini anak terakhir
        """

        # Tentukan karakter cabang
        branch = "└── " if is_last else "├── "
        print(prefix + branch + self.value)

        # Buat prefix baru untuk anak-anak
        if is_last:
            new_prefix = prefix + "    "
        else:
            new_prefix = prefix + "│   "

        # Cetak anak-anak
        for i, child in enumerate(self.children):
            child.pretty_print(new_prefix, i == len(self.children) - 1)