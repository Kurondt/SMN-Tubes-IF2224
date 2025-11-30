from abc import ABC, abstractmethod

class ASTNode(ABC):
    """Base class for all AST Nodes."""
    def __init__(self, line=0, col=0):
        self.type = None # type code (1=int, 2=bool, ... see analyzer.py init)
        self.tab_index = None # index in the Symbol Table (tab)
        self.scope_level = None # lexical level (0=global)
        self.line = line
        self.col = col

    def __repr__(self):
        return self.__class__.__name__

class ProgramNode(ASTNode):
    def __init__(self, name, declarations, block, line=0, col=0):
        super().__init__(line, col)
        self.name = name
        self.declarations = declarations  # list of declaration nodes
        self.block = block # blockNode

    def __repr__(self):
        return f"ProgramNode(name='{self.name}')"

class BlockNode(ASTNode):
    def __init__(self, statements, line=0, col=0):
        super().__init__(line, col)
        self.statements = statements
        self.block_index = None # index in btab

    def __repr__(self):
        return f"BlockNode(stmts={len(self.statements)})"

class VarDeclNode(ASTNode):
    def __init__(self, name, var_type_name, line=0, col=0):
        super().__init__(line, col)
        self.name = name
        self.var_type_name = var_type_name

    def __repr__(self):
        return f"VarDecl(name='{self.name}', type='{self.var_type_name}', tab_idx={self.tab_index})"

class ConstDeclNode(ASTNode):
    def __init__(self, name, value, const_type, line=0, col=0):
        super().__init__(line, col)
        self.name = name
        self.value = value
        self.const_type = const_type

    def __repr__(self):
        return f"ConstDecl(name='{self.name}', val={self.value}, type={self.const_type})"

class TypeDeclNode(ASTNode):
    def __init__(self, name, type_def, line=0, col=0):
        super().__init__(line, col)
        self.name = name
        self.type_def = type_def

    def __repr__(self):
        return f"TypeDecl(name='{self.name}', def='{self.type_def}')"

class ProcedureDeclNode(ASTNode):
    def __init__(self, name, params, block, line=0, col=0):
        super().__init__(line, col)
        self.name = name
        self.params = params # list of VarDeclNode
        self.block = block # BlockNode

    def __repr__(self):
        return f"ProcDecl(name='{self.name}', params={len(self.params)})"

class FunctionDeclNode(ASTNode):
    def __init__(self, name, params, return_type, block, line=0, col=0):
        super().__init__(line, col)
        self.name = name
        self.params = params
        self.return_type = return_type
        self.block = block

    def __repr__(self):
        return f"FuncDecl(name='{self.name}', ret='{self.return_type}')"

class AssignNode(ASTNode):
    def __init__(self, target, value, line=0, col=0):
        super().__init__(line, col)
        self.target = target # VarNode or ArrayAccessNode
        self.value = value # expression

    def __repr__(self):
        return f"Assign(target={self.target}, value={self.value})"

class BinOpNode(ASTNode):
    def __init__(self, op, left, right, line=0, col=0):
        super().__init__(line, col)
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinOp(op='{self.op}', left={self.left}, right={self.right}, type={self.type})"

class UnaryOpNode(ASTNode):
    def __init__(self, op, operand, line=0, col=0):
        super().__init__(line, col)
        self.op = op
        self.operand = operand

    def __repr__(self):
        return f"UnaryOp(op='{self.op}', operand={self.operand})"

class VarNode(ASTNode):
    def __init__(self, name, line=0, col=0):
        super().__init__(line, col)
        self.name = name

    def __repr__(self):
        return f"Var('{self.name}', tab_idx={self.tab_index}, type={self.type})"

class NumberNode(ASTNode):
    def __init__(self, value, line=0, col=0):
        super().__init__(line, col)
        self.value = value

    def __repr__(self):
        return f"Num({self.value})"

class StringNode(ASTNode):
    def __init__(self, value, line=0, col=0):
        super().__init__(line, col)
        self.value = value

    def __repr__(self):
        return f"String('{self.value}')"

class CharNode(ASTNode):
    def __init__(self, value, line=0, col=0):
        super().__init__(line, col)
        self.value = value

    def __repr__(self):
        return f"Char('{self.value}')"

class BooleanNode(ASTNode):
    def __init__(self, value, line=0, col=0):
        super().__init__(line, col)
        self.value = value

    def __repr__(self):
        return f"Bool({self.value})"

class ProcCallNode(ASTNode):
    def __init__(self, name, args, line=0, col=0):
        super().__init__(line, col)
        self.name = name
        self.args = args

    def __repr__(self):
        return f"ProcCall(name='{self.name}', args={self.args})"

class IfNode(ASTNode):
    def __init__(self, condition, then_stmt, else_stmt=None, line=0, col=0):
        super().__init__(line, col)
        self.condition = condition
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

    def __repr__(self):
        return f"If(cond={self.condition}, then={self.then_stmt}, else={self.else_stmt})"

class WhileNode(ASTNode):
    def __init__(self, condition, body, line=0, col=0):
        super().__init__(line, col)
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"While(cond={self.condition})"

class ForNode(ASTNode):
    def __init__(self, iterator, start_expr, end_expr, direction, body, line=0, col=0):
        super().__init__(line, col)
        self.iterator = iterator # VarNode
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.direction = direction # 'to' or 'downto'
        self.body = body

    def __repr__(self):
        return f"For(iter={self.iterator.name}, dir={self.direction})"

class ArrayAccessNode(ASTNode):
    def __init__(self, name, index_expr, line=0, col=0):
        super().__init__(line, col)
        self.name = name
        self.index_expr = index_expr

    def __repr__(self):
        return f"ArrayAccess(name='{self.name}', index={self.index_expr})"
