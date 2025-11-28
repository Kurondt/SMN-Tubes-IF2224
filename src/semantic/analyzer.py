import re
from src.parser.parsertree import ParseTree
from src.semantic.ast_nodes import *
from src.errors import SemanticError
from src.lexer.token import Token

class SemanticAnalyzer:
    def __init__(self):
        self.tab = []
        self.btab = []
        self.atab = [] # stores {xtyp, etyp, low, high, elsz, size}
        self.display = []
        self.level = 0
        self.types = {
            "integer": 1,
            "boolean": 2,
            "char": 3,
            "real": 4,
            "string": 5,
            "array": 6
        }
        self.init_tables()

    def init_tables(self):
        # initialize reserved slots
        for i in range(29):
            self.tab.append(None)
        
        # standard types
        self._set_reserved(1, "integer", "type", 1)
        self._set_reserved(2, "boolean", "type", 2)
        self._set_reserved(3, "char", "type", 3)
        self._set_reserved(4, "real", "type", 4)
        self._set_reserved(5, "string", "type", 5)
        self._set_reserved(6, "array", "type", 6)  
        
        self._set_reserved(7, "false", "constant", 2, val=0)
        self._set_reserved(8, "true", "constant", 2, val=1)

        std_funcs = [
            (9, "abs", 0), (10, "sqr", 0), (11, "odd", 2), (12, "chr", 3), 
            (13, "ord", 1), (14, "succ", 0), (15, "pred", 0), (16, "round", 1), 
            (17, "trunc", 1), (18, "sin", 4), (19, "cos", 4), (20, "exp", 4), 
            (21, "ln", 4), (22, "sqrt", 4), (23, "arctan", 4), (24, "eof", 2), 
            (25, "eoln", 2)
        ]

        for idx, name, ret_type in std_funcs:
            self._set_reserved(idx, name, "function", ret_type)
        
        # standard procedures
        self._set_reserved(26, "write", "procedure", 0)
        self._set_reserved(27, "writeln", "procedure", 0)
        self._set_reserved(28, "read", "procedure", 0)

        # just to be safe
        if len(self.tab) < 30:
             self.tab.append(None)
             self.tab.append(None)
        
        self._set_reserved(29, "readln", "procedure", 0)

         # global block
        self.btab.append({"last": 0, "lpar": 0, "psze": 0, "vsze": 0})
        self.display.append(0) 

    def _set_reserved(self, index, name, obj_type, type_code, val=0):
        while len(self.tab) <= index:
            self.tab.append(None)
            
        self.tab[index] = {
            "id": name, "obj": obj_type, "type": type_code, 
            "ref": 0, "nrm": 1, "lev": 0, "adr": val, "link": 0
        }

    def add_to_tab(self, name, obj_type, type_code, line=0, col=0, ref=0, val=0):
        current_block_idx = self.display[self.level]
        last_idx = self.btab[current_block_idx]["last"]
        
        # duplicate check
        curr = last_idx
        while curr > 0:
            if self.tab[curr]["id"] == name:
                 raise SemanticError(f"Duplicate identifier '{name}' in current scope.", line, col)
            curr = self.tab[curr]["link"]

        new_entry = {
            "id": name,
            "obj": obj_type,
            "type": type_code,
            "ref": ref,
            "nrm": 1,
            "lev": self.level,
            "adr": val,
            "link": last_idx
        }
        
        self.tab.append(new_entry)
        new_index = len(self.tab) - 1
        self.btab[current_block_idx]["last"] = new_index
        
        if obj_type == "variable":
            self.btab[current_block_idx]["vsze"] += 1
            
        return new_index

    def lookup(self, name, line=0, col=0):
        current_lev = self.level
        
        # search dynamic scopes
        while current_lev >= 0:
            block_idx = self.display[current_lev]
            curr = self.btab[block_idx]["last"]
            while curr > 0:
                entry = self.tab[curr]
                if entry and entry["id"] == name:
                    return curr, entry
                curr = entry["link"]
            current_lev -= 1
            
        # search reserved
        for i in range(1, 29):
            if self.tab[i] and self.tab[i]["id"] == name:
                return i, self.tab[i]
        
        raise SemanticError(f"Identifier '{name}' undeclared.", line, col)

    # helpers
    def _get_val(self, node: ParseTree):
        val = node.value
        if hasattr(val, 'value'): return val.value
        if isinstance(val, str):
            if "(" in val and val.endswith(")"):
                start = val.find("(")
                return val[start+1:-1]
            return val
        return str(val)

    def _get_pos(self, node: ParseTree):
        if hasattr(node, 'line') and node.line is not None:
            return node.line, node.col
        return 0, 0

    def _extract_simple_int(self, expr_node):
        # heuristic to extract int from expression tree
        # Tree: <expression> -> <simple> -> <term> -> <factor> -> NUMBER
        try:
            # expr -> simple
            simple = expr_node.children[0]
            # simple -> term
            term = simple.children[0]
            # term -> factor
            factor = term.children[0]
            # factor -> NUMBER(5) or similar
            # The value is inside the CHILD of factor, not factor itself
            number_node = factor.children[0]
            val = self._get_val(number_node)
            return int(val)
        except:
            return 0

    def _process_array_type(self, node: ParseTree):
        # <array_type> -> larik [ range ] dari type
        type_node = node.children[5]
        
        # get element type
        inner_type = type_node.children[0]
        type_name = self._get_val(inner_type)
        etyp_code = self.types.get(type_name.lower(), 0)
        
        # simplified bounds extraction
        range_node = node.children[2]
        low = 0
        high = 0
        
        try:
            val1 = self._extract_simple_int(range_node.children[0])
            low = val1
            val2 = self._extract_simple_int(range_node.children[2])
            high = val2
        except:
            pass 
            
        entry = {
            "xtyp": 1, # index type integer
            "etyp": etyp_code,
            "low": low,
            "high": high,
            "elsz": 1,
            "size": (high - low + 1)
        }
        
        self.atab.append(entry)
        return len(self.atab) - 1

    # visitors

    def analyze(self, parse_tree: ParseTree):
        if parse_tree.value == "<program>":
            return self.visit_program(parse_tree)
        raise SemanticError("Invalid Root Node", 0, 0)

    def visit_program(self, node: ParseTree):
        header_node = node.children[0]
        decl_node = node.children[1]
        compound_node = node.children[2]
        
        id_node = header_node.children[1]
        prog_name = self._get_val(id_node)
        line, col = self._get_pos(id_node)
        
        self.add_to_tab(prog_name, "program", 0, line, col)

        declarations = self.visit_declarations(decl_node)

        self.level += 1
        self.btab.append({"last": 0, "lpar": 0, "psze": 0, "vsze": 0})
        self.display.append(len(self.btab) - 1)
        
        main_block_ast = self.visit_compound_statement(compound_node)
        main_block_ast.block_index = self.display[self.level]
        
        self.display.pop()
        self.level -= 1
        
        return ProgramNode(prog_name, declarations, main_block_ast, line, col)

    def visit_declarations(self, node: ParseTree):
        decls = []
        for child in node.children:
            val = self._get_val(child)
            if val == "<var_declaration>":
                decls.extend(self.visit_var_declaration(child))
            elif val == "<const_declaration>":
                decls.extend(self.visit_const_declaration(child))
            elif val == "<type_declaration>":
                decls.extend(self.visit_type_declaration(child))
            elif val == "<subprogram_declaration>":
                res = self.visit_subprogram_declaration(child)
                if res: decls.append(res)
        return decls

    def visit_const_declaration(self, node: ParseTree):
        generated = []
        i = 1 
        while i < len(node.children):
            id_node = node.children[i]
            val_node = node.children[i+2]
            
            name = self._get_val(id_node)
            line, col = self._get_pos(id_node)
            
            val_token = self._get_val(val_node)
            const_type = 0
            stored_val = 0
            
            # infer type
            if "NUMBER" in str(val_node.value) or val_token.replace('.','',1).isdigit():
                if '.' in val_token:
                    const_type = 4 
                    stored_val = float(val_token)
                else:
                    const_type = 1 
                    stored_val = int(val_token)
            elif "STRING" in str(val_node.value) or val_token.startswith("'"):
                content = val_token.strip("'")
                if len(content) == 1:
                    const_type = 3 
                    stored_val = ord(content)
                else:
                    const_type = 5 
                    stored_val = 0
            elif "CHAR" in str(val_node.value):
                const_type = 3
                stored_val = ord(val_token.strip("'")[0])
            
            self.add_to_tab(name, "constant", const_type, line, col, val=stored_val)
            generated.append(ConstDeclNode(name, val_token, const_type, line, col))
            i += 4
            
        return generated

    def visit_type_declaration(self, node: ParseTree):
        generated = []
        i = 1
        while i < len(node.children):
            id_node = node.children[i]
            def_node = node.children[i+2]
            
            name = self._get_val(id_node)
            line, col = self._get_pos(id_node)
            
            type_node = def_node.children[0]
            type_node_val = self._get_val(type_node)
            
            resolved_type_code = 0
            ref_idx = 0
            
            if type_node_val == "<type>":
                inner = type_node.children[0]
                inner_val = self._get_val(inner)
                
                if inner_val == "<array_type>":
                    resolved_type_code = 6 
                    ref_idx = self._process_array_type(inner)
                else:
                    resolved_type_code = self.types.get(inner_val.lower(), 0)
            
            elif type_node_val == "<record_type>":
                pass 

            self.add_to_tab(name, "type", resolved_type_code, line, col, ref=ref_idx)
            generated.append(TypeDeclNode(name, "alias", line, col))
            
            i += 4
        return generated

    def visit_var_declaration(self, node: ParseTree):
        generated_nodes = []
        i = 1 
        while i < len(node.children):
            ident_list_node = node.children[i]
            type_node = node.children[i+2]
            
            type_child = type_node.children[0]
            type_code = 0
            ref_idx = 0
            type_name = "unknown"
            type_val = self._get_val(type_child)
            
            if type_val == "<array_type>":
                type_name = "array" 
                type_code = 6 
                ref_idx = self._process_array_type(type_child)
            else:
                type_name = type_val
                type_code = self.types.get(type_name.lower(), 0)
                if type_code == 0:
                     try:
                        _, info = self.lookup(type_name)
                        if info['obj'] == 'type':
                            type_code = info['type']
                            ref_idx = info['ref'] 
                        else:
                             line, col = self._get_pos(type_child)
                             raise SemanticError(f"'{type_name}' is not a type.", line, col)
                     except SemanticError:
                         line, col = self._get_pos(type_child)
                         raise SemanticError(f"Error: Unknown type '{type_name}'", line, col)
            
            idents_info = self.visit_identifier_list(ident_list_node)
            for name, line, col in idents_info:
                idx = self.add_to_tab(name, "variable", type_code, line, col, ref=ref_idx)
                var_node = VarDeclNode(name, type_name, line, col)
                var_node.tab_index = idx
                var_node.scope_level = self.level
                generated_nodes.append(var_node)
            i += 4 
        return generated_nodes

    def visit_subprogram_declaration(self, node: ParseTree):
        child = node.children[0]
        val = self._get_val(child)
        
        if val == "<procedure_declaration>":
             return self.visit_procedure_decl(child)
        elif val == "<function_declaration>":
             return self.visit_function_decl(child)
        return None

    def visit_formal_parameter_list(self, node: ParseTree):
        params = []
        for child in node.children:
            if self._get_val(child) == "<parameter_group>":
                params.extend(self.visit_parameter_group(child))
        return params

    def visit_parameter_group(self, node: ParseTree):
        id_list_node = node.children[0]
        type_node = node.children[2]
        
        type_child = type_node.children[0]
        type_val = self._get_val(type_child)
        type_code = self.types.get(type_val.lower(), 0)
        
        if type_code == 0:
             line, col = self._get_pos(type_child)
             raise SemanticError(f"Unknown type '{type_val}' in parameter list", line, col)

        ids = self.visit_identifier_list(id_list_node)
        generated = []
        
        for name, line, col in ids:
            # add params as vars to current scope
            self.add_to_tab(name, "variable", type_code, line, col)
            current_block_idx = self.display[self.level]
            self.btab[current_block_idx]["psze"] += 1 
            generated.append(VarDeclNode(name, type_val, line, col))
            
        return generated

    def visit_procedure_decl(self, node: ParseTree):
        id_node = node.children[1]
        name = self._get_val(id_node)
        line, col = self._get_pos(id_node)
        
        self.add_to_tab(name, "procedure", 0, line, col)
        
        # enter scope
        self.level += 1
        self.btab.append({"last": 0, "lpar": 0, "psze": 0, "vsze": 0})
        self.display.append(len(self.btab) - 1)
        
        params = []
        possible_params = node.children[2]
        if self._get_val(possible_params) == "<formal_parameter_list>":
            params = self.visit_formal_parameter_list(possible_params)
            block_node_idx = 4
        else:
            block_node_idx = 3
            
        block_node = node.children[block_node_idx]
        if self._get_val(block_node.children[0]) == "<declaration_part>":
            self.visit_declarations(block_node.children[0])
            body_node = block_node.children[1]
        else:
            body_node = block_node.children[0]
            
        body_ast = self.visit_compound_statement(body_node)
        
        self.display.pop()
        self.level -= 1
        
        return ProcedureDeclNode(name, params, body_ast, line, col)

    def visit_function_decl(self, node: ParseTree):
        id_node = node.children[1]
        name = self._get_val(id_node)
        line, col = self._get_pos(id_node)
        
        has_params = (self._get_val(node.children[2]) == "<formal_parameter_list>")
        type_node_idx = 4 if has_params else 3
        block_node_idx = 6 if has_params else 5
        
        type_node = node.children[type_node_idx] 
        type_keyword = type_node.children[0]
        type_name = self._get_val(type_keyword)
        ret_type_code = self.types.get(type_name.lower(), 0)
        
        self.add_to_tab(name, "function", ret_type_code, line, col)
        
        # enter scope
        self.level += 1
        self.btab.append({"last": 0, "lpar": 0, "psze": 0, "vsze": 0})
        self.display.append(len(self.btab) - 1)
        
        params = []
        if has_params:
            params = self.visit_formal_parameter_list(node.children[2])
        
        block_node = node.children[block_node_idx]
        if self._get_val(block_node.children[0]) == "<declaration_part>":
            self.visit_declarations(block_node.children[0])
            body_node = block_node.children[1]
        else:
            body_node = block_node.children[0]
            
        body_ast = self.visit_compound_statement(body_node)
        
        self.display.pop()
        self.level -= 1
        
        return FunctionDeclNode(name, params, type_name, body_ast, line, col)

    def visit_identifier_list(self, node: ParseTree):
        infos = []
        for child in node.children:
            val = self._get_val(child)
            if val != "," and val != "<identifier_list>": 
                 line, col = self._get_pos(child)
                 infos.append((val, line, col))
        return infos

    def visit_compound_statement(self, node: ParseTree):
        stmt_list_node = node.children[1]
        line, col = self._get_pos(node)
        stmts = self.visit_statement_list(stmt_list_node)
        return BlockNode(stmts, line, col)

    def visit_statement_list(self, node: ParseTree):
        stmts = []
        for child in node.children:
            val = self._get_val(child)
            if val == "<statement>":
                res = self.visit_statement(child)
                if res: stmts.append(res)
        return stmts

    def visit_statement(self, node: ParseTree):
        child = node.children[0]
        val = self._get_val(child)
        if val == "<assignment-statement>": return self.visit_assignment(child)
        elif val == "<procedure/function-call>": return self.visit_proc_call(child)
        elif val == "<compound_statement>": return self.visit_compound_statement(child)
        elif val == "<if-statement>": return self.visit_if(child)
        elif val == "<while-statement>": return self.visit_while(child)
        elif val == "<for-statement>": return self.visit_for(child)
        return None

    def visit_assignment(self, node: ParseTree):
        id_node = node.children[0]
        target_name = self._get_val(id_node)
        line, col = self._get_pos(id_node)
        
        has_bucket = (len(node.children) > 1 and self._get_val(node.children[1]) == "<array-bucket>")
        assign_op_idx = 2 if has_bucket else 1
        expr_idx = assign_op_idx + 1
        
        idx, info = self.lookup(target_name, line, col)
        target_type = info['type']
        
        if has_bucket:
             bucket_node = node.children[1]
             content_node = bucket_node.children[1] 
             
             idx_val = self._get_val(content_node)
             idx_line, idx_col = self._get_pos(content_node)
             
             if idx_val.replace('.', '', 1).isdigit():
                 idx_expr = NumberNode(int(idx_val), idx_line, idx_col)
                 idx_expr.type = 1
             elif idx_val[0].isalpha():
                 idx_expr = VarNode(idx_val, idx_line, idx_col)
                 i_idx, i_info = self.lookup(idx_val, idx_line, idx_col)
                 idx_expr.tab_index = i_idx
                 idx_expr.type = i_info['type']
             else:
                 idx_expr = NumberNode(0, idx_line, idx_col) # simplified fallback

             # check element type from atab if array
             if info['type'] == 6: 
                 atab_idx = info['ref']
                 if 0 <= atab_idx < len(self.atab):
                     target_type = self.atab[atab_idx]['etyp']
                 else:
                     raise SemanticError("Invalid array reference in symbol table", line, col)
             else:
                 raise SemanticError(f"Variable '{target_name}' is not an array.", line, col)

             target_node = ArrayAccessNode(target_name, idx_expr, line, col)
             target_node.tab_index = idx
             target_node.type = target_type 
        else:
             target_node = VarNode(target_name, line, col)
             target_node.tab_index = idx
             target_node.type = info['type']

        expr_node = self.visit_expression(node.children[expr_idx])
        
        if info['obj'] == 'constant':
            raise SemanticError(f"Cannot assign to constant '{target_name}'", line, col)

        if target_node.type != expr_node.type:
             if not (target_node.type == 4 and expr_node.type == 1):
                 raise SemanticError(f"Type Mismatch: Cannot assign type {expr_node.type} to variable '{target_name}' of type {target_node.type}", line, col)

        return AssignNode(target_node, expr_node, line, col)

    def visit_expression(self, node: ParseTree):
        left = self.visit_simple_expression(node.children[0])
        if len(node.children) > 1:
            rel_node = node.children[1]
            op_node = rel_node.children[0]
            op = self._get_val(op_node)
            line, col = self._get_pos(op_node)
            right = self.visit_simple_expression(node.children[2])
            bin_node = BinOpNode(op, left, right, line, col)
            bin_node.type = 2 
            return bin_node
        return left

    def visit_simple_expression(self, node: ParseTree):
        children = node.children
        idx = 0
        first_node = children[0]
        first_val = self._get_val(first_node)
        
        if first_val in ["+", "-"] or (hasattr(first_node.value, 'type') and first_node.value.type == "ARITHMETIC_OPERATOR"):
            sign = first_val
            line, col = self._get_pos(first_node)
            idx += 1
            term = self.visit_term(children[idx])
            left = UnaryOpNode(sign, term, line, col)
            left.type = term.type
            idx += 1
        else:
            left = self.visit_term(children[idx])
            idx += 1
            
        while idx < len(children):
            op_node = children[idx].children[0]
            op = self._get_val(op_node)
            line, col = self._get_pos(op_node)
            right = self.visit_term(children[idx+1])
            new_node = BinOpNode(op, left, right, line, col)
            
            is_int = (left.type == 1 and right.type == 1)
            is_real = (left.type in [1, 4] and right.type in [1, 4])
            
            if op in ['+', '-', 'atau', 'or']:
                if op in ['atau', 'or']:
                    if left.type != 2 or right.type != 2:
                        raise SemanticError(f"Operator '{op}' requires boolean operands", line, col)
                    new_node.type = 2
                else:
                    if not is_real:
                        raise SemanticError(f"Operator '{op}' requires numeric operands", line, col)
                    new_node.type = 1 if is_int else 4

            left = new_node
            idx += 2
        return left

    def visit_term(self, node: ParseTree):
        left = self.visit_factor(node.children[0])
        idx = 1
        while idx < len(node.children):
            op_node = node.children[idx].children[0]
            op = self._get_val(op_node)
            line, col = self._get_pos(op_node)
            right = self.visit_factor(node.children[idx+1])
            new_node = BinOpNode(op, left, right, line, col)
            
            is_int = (left.type == 1 and right.type == 1)
            is_real = (left.type in [1, 4] and right.type in [1, 4])

            if op == "/": 
                if not is_real: raise SemanticError(f"Operator '/' requires numeric operands", line, col)
                new_node.type = 4 
            elif op in ["div", "mod"]: 
                if not is_int: raise SemanticError(f"Operator '{op}' requires integer operands", line, col)
                new_node.type = 1 
            elif op in ["*", "dan", "and"]:
                 if op in ["dan", "and"]:
                    if left.type != 2 or right.type != 2:
                        raise SemanticError(f"Operator '{op}' requires boolean operands", line, col)
                    new_node.type = 2
                 else:
                    if not is_real: raise SemanticError(f"Operator '*' requires numeric operands", line, col)
                    new_node.type = 1 if is_int else 4
            elif op == "bagi":
                 if not is_real: raise SemanticError(f"Operator '{op}' requires numeric operands", line, col)
                 new_node.type = 4
            
            left = new_node
            idx += 2
        return left

    def visit_factor(self, node: ParseTree):
        child = node.children[0]
        val = self._get_val(child)
        line, col = self._get_pos(child)
        
        # logical not
        if hasattr(child.value, 'type') and child.value.type == "LOGICAL_OPERATOR" and val in ["tidak", "not"]:
             operand = self.visit_factor(node.children[1])
             if operand.type != 2:
                 raise SemanticError(f"Operator '{val}' requires boolean operand", line, col)
             un_op = UnaryOpNode(val, operand, line, col)
             un_op.type = 2
             return un_op
        elif val in ["tidak", "not"]: 
             operand = self.visit_factor(node.children[1])
             un_op = UnaryOpNode(val, operand, line, col)
             un_op.type = 2
             return un_op

        token_type = ""
        if hasattr(child.value, 'type'):
             token_type = child.value.type
        else:
             if "NUMBER" in str(child.value): token_type = "NUMBER"
             elif "IDENTIFIER" in str(child.value): token_type = "IDENTIFIER"
             elif "STRING" in str(child.value): token_type = "STRING_LITERAL"
             elif "LPAREN" in str(child.value): token_type = "LPARENTHESIS"
        
        if token_type == "NUMBER" or val.replace('.', '', 1).isdigit():
            if '.' in val or 'e' in val.lower():
                n = NumberNode(float(val), line, col)
                n.type = 4
            else:
                n = NumberNode(int(val), line, col)
                n.type = 1
            return n
            
        elif token_type == "IDENTIFIER" or (val and val[0].isalpha()):
            if len(node.children) > 1 and self._get_val(node.children[1]) == "<procedure/function-call>":
                 return self.visit_proc_call(node.children[0])
            
            # array access check
            if len(node.children) > 1 and self._get_val(node.children[1]) == "<array-bucket>":
                bucket = node.children[1]
                content = bucket.children[1]
                idx_val = self._get_val(content)
                idx_line, idx_col = self._get_pos(content)
                
                if idx_val.replace('.', '', 1).isdigit():
                    idx_expr = NumberNode(int(idx_val), idx_line, idx_col)
                    idx_expr.type = 1
                else:
                    idx_idx, idx_info = self.lookup(idx_val, idx_line, idx_col)
                    idx_expr = VarNode(idx_val, idx_line, idx_col)
                    idx_expr.tab_index = idx_idx
                    idx_expr.type = idx_info['type']
                
                arr_idx, arr_info = self.lookup(val, line, col)
                
                elem_type = 0
                if arr_info['type'] == 6: 
                    atab_idx = arr_info['ref']
                    if 0 <= atab_idx < len(self.atab):
                        elem_type = self.atab[atab_idx]['etyp']
                
                access = ArrayAccessNode(val, idx_expr, line, col)
                access.tab_index = arr_idx
                access.type = elem_type
                return access

            idx, info = self.lookup(val, line, col)

            if info['obj'] == 'constant':
                if info['type'] == 2: 
                     b = BooleanNode(True if info['adr'] == 1 else False, line, col)
                     b.type = 2
                     return b
                elif info['type'] == 1: 
                     n = NumberNode(info['adr'], line, col)
                     n.type = 1
                     return n
            
            v = VarNode(val, line, col)
            v.tab_index = idx
            v.type = info['type']
            return v
            
        elif token_type == "STRING_LITERAL" or val.startswith("'"):
            content = val.strip("'")
            if len(content) == 1:
                s = CharNode(content, line, col)
                s.type = 3
            else:
                s = StringNode(content, line, col)
                s.type = 5
            return s
            
        elif token_type == "LPARENTHESIS" or val == "(":
            return self.visit_expression(node.children[1])
            
        elif val == "<procedure/function-call>":
             return self.visit_proc_call(child)
        
        return NumberNode(0, line, col)

    def visit_proc_call(self, node: ParseTree):
        id_node = node.children[0]
        name = self._get_val(id_node)
        line, col = self._get_pos(id_node)
        
        idx, info = self.lookup(name, line, col) 
        
        args = []
        if len(node.children) > 3:
             param_node = node.children[2]
             if self._get_val(param_node) == "<parameter-list>":
                 args = self.visit_param_list(param_node)
        
        node = ProcCallNode(name, args, line, col)
        if info['obj'] == 'function':
            node.type = info['type']
        else:
            node.type = 0 
            
        return node

    def visit_param_list(self, node: ParseTree):
        args = []
        for child in node.children:
            val = self._get_val(child)
            if val == "<expression>":
                args.append(self.visit_expression(child))
            elif val.startswith("'") or "STRING" in str(child.value):
                line, col = self._get_pos(child)
                s = StringNode(val.strip("'"), line, col)
                s.type = 5
                args.append(s)
        return args
    
    def visit_if(self, node: ParseTree):
        line, col = self._get_pos(node)
        condition = self.visit_expression(node.children[1])
        then_stmt = self.visit_statement(node.children[3])
        else_stmt = None
        if len(node.children) > 4:
            else_stmt = self.visit_statement(node.children[5])
        return IfNode(condition, then_stmt, else_stmt, line, col)

    def visit_while(self, node: ParseTree):
        line, col = self._get_pos(node)
        cond = self.visit_expression(node.children[1])
        body = self.visit_statement(node.children[3])
        return WhileNode(cond, body, line, col)

    def visit_for(self, node: ParseTree):
        line, col = self._get_pos(node)
        iter_node = node.children[1]
        iter_name = self._get_val(iter_node)
        iter_pos = self._get_pos(iter_node)
        
        idx, info = self.lookup(iter_name, iter_pos[0], iter_pos[1])
        iter_ast = VarNode(iter_name, iter_pos[0], iter_pos[1])
        iter_ast.tab_index = idx
        
        start_expr = self.visit_expression(node.children[3])
        
        dir_val = self._get_val(node.children[4])
        direction = "to" if "ke" in dir_val else "downto"
        
        end_expr = self.visit_expression(node.children[5])
        body = self.visit_statement(node.children[7])
        
        return ForNode(iter_ast, start_expr, end_expr, direction, body, line, col)

    # printing things

    def print_output(self, ast):
        # tab output
        print("\nOutput")
        print("tabs:")
        tab_headers = ["idx", "id", "obj", "type", "ref", "nrm", "lev", "adr", "link"]
        tab_widths = [4, 15, 12, 6, 6, 4, 4, 6, 6]
        self._print_table_header(tab_headers, tab_widths)
        
        for i, entry in enumerate(self.tab):
            if entry:
                row = entry.copy()
                row['idx'] = i
                self._print_row(row, tab_headers, tab_widths)

        # btab output
        print("\nbtab:")
        btab_headers = ["idx", "last", "lpar", "psze", "vsze"]
        btab_widths = [4, 6, 6, 6, 6]
        self._print_table_header(btab_headers, btab_widths)
        for i, entry in enumerate(self.btab):
            row = entry.copy()
            row['idx'] = i
            self._print_row(row, btab_headers, btab_widths)

        # atab output
        print("\natab:")
        atab_headers = ["idx", "xtyp", "etyp", "low", "high", "elsz", "size"]
        atab_widths = [4, 6, 6, 6, 6, 6, 6]
        
        if not self.atab:
            print("(empty because no array)")
        else:
            self._print_table_header(atab_headers, atab_widths)
            for i, entry in enumerate(self.atab):
                row = entry.copy()
                row['idx'] = i
                self._print_row(row, atab_headers, atab_widths)

        # decorated ast output
        print("\nDecorated AST:")
        self._print_decorated_ast(ast)

    def _print_table_header(self, headers, widths):
        header_str = "  ".join(f"{h:<{w}}" for h, w in zip(headers, widths))
        print(header_str)
        print("-" * len(header_str))

    def _print_row(self, row, headers, widths):
        row_str = "  ".join(f"{str(row.get(h, '')):<{w}}" for h, w in zip(headers, widths))
        print(row_str)

    def _print_decorated_ast(self, node, prefix="", is_last=True):
        rev_types = {v: k for k, v in self.types.items()}
        rev_types[0] = "void/none" 

        def get_type_name(code):
            return rev_types.get(code, str(code))

        branch = "└─ " if is_last else "├─ "
        
        label = ""
        if hasattr(node, 'name'):
            label = f"{node.__class__.__name__}('{node.name}')"
        elif hasattr(node, 'value'):
            label = f"{node.__class__.__name__} {node.value}"
        elif hasattr(node, 'op'):
            label = f"{node.__class__.__name__} '{node.op}'"
        elif hasattr(node, 'statements'):
            label = "Block"
        else:
            label = node.__class__.__name__

        notes = []
        if node.tab_index is not None:
            notes.append(f"tab_index:{node.tab_index}")
        if node.type is not None:
            notes.append(f"type:{get_type_name(node.type)}")
        if node.scope_level is not None:
            notes.append(f"lev:{node.scope_level}")
        if hasattr(node, 'block_index') and node.block_index is not None:
            notes.append(f"block_index:{node.block_index}")
        
        annotation = f" → {', '.join(notes)}" if notes else ""

        print(prefix + branch + label + annotation)

        children = []
        if hasattr(node, 'declarations'): children.extend(node.declarations)
        if hasattr(node, 'block') and node.block: children.append(node.block)
        if hasattr(node, 'statements'): children.extend(node.statements)
        if hasattr(node, 'target'): children.append(node.target)
        if hasattr(node, 'value') and isinstance(node.value, object) and hasattr(node.value, 'type'): 
                children.append(node.value)
        if hasattr(node, 'left'): children.append(node.left)
        if hasattr(node, 'right'): children.append(node.right)
        if hasattr(node, 'operand'): children.append(node.operand)
        if hasattr(node, 'args'): children.extend(node.args)
        if hasattr(node, 'condition'): children.append(node.condition)
        if hasattr(node, 'then_stmt'): children.append(node.then_stmt)
        if hasattr(node, 'else_stmt') and node.else_stmt: children.append(node.else_stmt)
        if hasattr(node, 'start_expr'): children.append(node.start_expr)
        if hasattr(node, 'end_expr'): children.append(node.end_expr)
        if hasattr(node, 'body'): children.append(node.body)
        if hasattr(node, 'iterator'): children.append(node.iterator)
        if hasattr(node, 'index_expr'): children.append(node.index_expr)

        if is_last:
            new_prefix = prefix + "   "
        else:
            new_prefix = prefix + "│  "

        for i, child in enumerate(children):
            self._print_decorated_ast(child, new_prefix, i == len(children) - 1)
