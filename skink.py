#######################################
# IMPORTS
#######################################
import numpy as np 
import uuid
import string

#######################################
# CONSTANTS
#######################################
DIGITS = '0123456789'
LETTERS = string.ascii_letters + '_'
LETTERS_DIGITS = LETTERS + DIGITS
NEWLINES = '\n\r;'
DEFAULT_MAX_DEPTH = 9

#######################################
# ERRORS
#######################################

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result  = f'{self.pos_start.fn}:{self.pos_start.ln + 1}:{self.pos_start.col + 1}: '
        result  += f'{self.error_name}: {self.details}'
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)


class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'Runtime Error', details)
        self.context = context

    def as_string(self):
        result  = f'{self.pos_start.fn}:{self.pos_start.ln + 1}:{self.pos_start.col + 1}: '
        result  += f'{self.error_name}: {self.details}\n'
        result  += 'stack traceback: '
        result  += self.generate_traceback()
        return result

    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = f'{result}\n\t{pos.fn}:{pos.ln + 1}:{pos.col + 1}: in {ctx.display_name}'
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return result

    


#######################################
# POSITION
#######################################

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char):
        self.idx += 1
        self.col += 1

        if current_char != None and current_char in NEWLINES:
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

#######################################
# TOKENS
#######################################

TT_INT		= 'INT'
TT_FLOAT    = 'FLOAT'
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD  = 'KEYWORD'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_EQ       = 'EQ'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'
TT_EE       = 'EE'
TT_NE       = 'NE'
TT_LT       = 'LT'
TT_LTE      = 'LTE'
TT_GT       = 'GT'
TT_GTE      = 'GTE'
TT_AND      = 'AND'
TT_OR       = 'OR'
TT_XOR      = 'XOR'
TT_NOT      = 'NOT'
TT_BAND     = 'BAND'
TT_BOR      = 'BOR'
TT_BXOR     = 'BXOR'
TT_BNOT     = 'BNOT'
TT_NEWLINE  = 'NEWLINE'
TT_EOF      = 'EOF'
KEYWORDS = [
    'var',
    'null'
]

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value


        if pos_end:
            self.pos_end = pos_end

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance(None)

    def display_text(self):
        if self.type == TT_EOF: return 'end of input'
        return f'token "{self.pos_start.ftxt[self.pos_start.idx:self.pos_end.idx]}"'
        
    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
    
#######################################
# LEXER
#######################################

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == '!':
                tokens.append(self.make_not_equals())
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
            elif self.current_char == '&':
                tokens.append(self.make_and())
            elif self.current_char == '|':
                tokens.append(self.make_or())
            elif self.current_char == '^':
                tokens.append(self.make_xor())
            elif self.current_char == '~':
                tokens.append(Token(TT_BNOT, pos_start=self.pos))
                self.advance()
            elif self.current_char in NEWLINES:
                tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, f'"{char}"')

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            clipped = np.clip(int(num_str), -(2 ** 63), 2 ** 63 - 1)
            return Token(TT_INT, np.int64(clipped), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS:
            id_str += self.current_char
            self.advance()

        tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos)

    def make_not_equals(self):
        tok_type = TT_NOT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_NE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)
        

    def make_equals(self):
        tok_type = TT_EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_EE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self):
        tok_type = TT_LT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_LTE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_greater_than(self):
        tok_type = TT_GT
        pos_start = self.pos.copy()
        print(self.current_char)
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_GTE

        print(self.current_char)
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_and(self):
        tok_type = TT_BAND
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '&':
            self.advance()
            tok_type = TT_AND

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_or(self):
        tok_type = TT_BOR
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '|':
            self.advance()
            tok_type = TT_OR

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_xor(self):
        tok_type = TT_BXOR
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '^':
            self.advance()
            tok_type = TT_XOR

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

#######################################
# NODES
#######################################
class NullNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end
    
    def __repr__(self):
        return f'{self.tok}'

class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end
    
    def __repr__(self):
        return f'{self.tok}'

class VarAccessNode:
	def __init__(self, var_name_tok):
		self.var_name_tok = var_name_tok

		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.var_name_tok.pos_end

class VarDeclareNode:
	def __init__(self, var_name_tok, value_node):
		self.var_name_tok = var_name_tok
		self.value_node = value_node

		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.value_node.pos_end


class StatementsNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes

        self.pos_start = pos_start
        self.pos_end = pos_end


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = left_node.pos_start
        self.pos_end = right_node.pos_end
    
    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = op_tok.pos_start
        self.pos_end = node.pos_end




    def __repr__(self):
        return f'({self.op_tok}, {self.node})'

#######################################
# PARSE RESULT
#######################################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        self.last_registered_advance_count = 1
        self.advance_count += 1

    def register(self, res):
        self.last_registered_advance_count = res.advance_count
        self.advance_count += res.advance_count
        if res.error: self.error = res.error
        return res.node

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.last_registered_advance_count == 0:
            self.error = error
        return self

#######################################
# PARSER
#######################################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        self.update_current_tok()
        return self.current_tok

    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    def update_current_tok(self):
        if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]


    def parse(self):
        res = self.statements()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f'Unexpected {self.current_tok.display_text()}'
            ))
        return res

    ###################################

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))
        
        elif tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.matches(TT_KEYWORD, 'null'):
            res.register_advancement()
            self.advance()
            return res.success(NullNode(tok))

        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f'Unexpected {self.current_tok.display_text()}'
                ))

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            f'Unexpected {self.current_tok.display_text()}'
        ))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def comp_expr(self):
        return self.bin_op(self.arith_expr, (TT_LT, TT_LTE, TT_GT, TT_GTE))
    
    def eq_expr(self):
        return self.bin_op(self.comp_expr, (TT_EQ, TT_NE))
    
    def band_expr(self):
        return self.bin_op(self.eq_expr, (TT_BAND, ))
    
    def bxor_expr(self):
        return self.bin_op(self.band_expr, (TT_BXOR, ))
    
    def bor_expr(self):
        return self.bin_op(self.bxor_expr, (TT_BOR, ))
    
    def and_expr(self):
        return self.bin_op(self.bor_expr, (TT_AND, ))
    
    def xor_expr(self):
        return self.bin_op(self.and_expr, (TT_XOR, ))
    
    def or_expr(self):
        return self.bin_op(self.xor_expr, (TT_OR, ))

    def assignment_expr(self):
        return self.bin_op(self.or_expr, (TT_EQ,))

    def expr(self):
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD, 'var'):
            var_declare_expr = res.register(self.var_declare_expr())
            if res.error: return res
            return res.success(var_declare_expr)

        return self.assignment_expr()

    def var_declare_expr(self):
        res = ParseResult()
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f'Unexpected {self.current_tok.display_text()}'
            ))
        
        var_name = self.current_tok
        
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_EQ:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f'Unexpected {self.current_tok.display_text()}'
            ))

        res.register_advancement()
        self.advance()

        expr = res.register(self.expr())
        if res.error: return res

        return res.success(VarDeclareNode(var_name, expr))
    

    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()
        
        statement = res.register(self.expr())
        if res.error: return res
        
        statements.append(statement)

        more_statements = True
        while True:
            newline_count = 0
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()
                newline_count += 1
            
            if newline_count == 0:
                more_statements = False
            
            if not more_statements: break
            statement = res.try_register(self.expr())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            else:
                statements.append(statement)


        return res.success(StatementsNode(
            statements,
            pos_start,
            self.current_tok.pos_end.copy()
        ))


    ###################################

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error: return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

#######################################
# RUNTIME RESULT
#######################################
class RTResult:
    def __init__(self):
        self.value = None
        self.error = None
    
    def register(self, res):
        if res.error: self.error = res.error
        return res.value

    def success(self, value):
        self.value = value
        return self
    
    def failure(self, error):
        self.error = error
        return self

#######################################
# VALUES
#######################################
class Object:
    def __init__(self, prototype=None):
        self.slots = {}
        self.prototype = prototype
        self.uuid = uuid.uuid4()

        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self
        
    def get(self, name):
        name = str(name)
        value = self.slots.get(name, None)
        if value == None and self.prototype:
            return self.prototype.get(name)
        return value

    def set(self, name, value):
        name = str(name)
        self.slots[name] = value

    def remove(self, name):
        del self.slots[name]

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        return None, self.illegal_operation(other)

    def multed_by(self, other):
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        return None, self.illegal_operation(other)
        
    def illegal_operation(self, other=None):
        if not other: other = self
        return RTError(
            self.pos_start, other.pos_end,
            'Illegal operation',
            self.context
        )
    
    def __repr__(self, depth_decr=DEFAULT_MAX_DEPTH):
        # print(depth_decr)
        if depth_decr < 0:
            return '{...}'

        keys = list(self.slots.keys())
        values = list(self.slots.values())

        if len(keys) == 0: return '{}'
        result = '{'
        for i in range(0, len(keys)-1):
            key = keys[i]
            value = values[i]

            value_str = value.__repr__(depth_decr - 1) if type(value) == Object else str(value)

            result += f'{key}: {value_str}, ' 
        
        key = keys[-1]
        value = values[-1]

        value_str = value.__repr__(depth_decr - 1) if type(value) == Object else str(value)

        result += f'{key}: {value_str}}}' 
        return result

class Null(Object):
    def __init__(self):
        super().__init__(null_object)
    
    def __repr__(self):
        return 'null'
        
class Int(Object): 
    def __init__(self, value):
        super().__init__(int_object)
        self.value = np.int64(value)
    
    def added_to(self, other): 
        if isinstance(other, (Int, Float)):
            result = self.value + other.value
            if isinstance(result, np.int64):
                return Int(result).set_context(self.context), None
            else:
                return Float(result).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)
                
    def subbed_by(self, other): 
        if isinstance(other, (Int, Float)):
            result = self.value - other.value
            if isinstance(result, np.int64):
                return Int(result).set_context(self.context), None
            else:
                return Float(result).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)
        
    def multed_by(self, other): 
        if isinstance(other, (Int, Float)):
            result = self.value * other.value
            if isinstance(result, np.int64):
                return Int(result).set_context(self.context), None
            else:
                return Float(result).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)
        
    def dived_by(self, other): 
        if isinstance(other, (Int, Float)):
            if repr(other) == '0':
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Integer division by zero',
                    self.context
                )
            elif repr(other) == '0.0':
                return Float(np.inf).set_context(self.context), None
            else:
                result = self.value / other.value if isinstance(other.value, float) else self.value // other.value
                if isinstance(result, np.int64):
                    return Int(result).set_context(self.context), None
                else:
                    return Float(result).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)
        
    def negated(self): 
        result = -self.value
        return Int(result).set_context(self.context), None

    def __repr__(self):
        return f'{self.value}'
        
    
class Float(Object): 
    def __init__(self, value):
        super().__init__(float_object)
        self.value = float(value)
    
    def added_to(self, other): 
        if isinstance(other, (Int, Float)):
            result = self.value + other.value
            if isinstance(result, np.int64):
                return Int(result).set_context(self.context), None
            else:
                return Float(result).set_context(self.context), None
                
    def subbed_by(self, other): 
        if isinstance(other, (Int, Float)):
            result = self.value - other.value
            if isinstance(result, np.int64):
                return Int(result).set_context(self.context), None
            else:
                return Float(result).set_context(self.context), None

    def multed_by(self, other): 
        if isinstance(other, (Int, Float)):
            result = self.value * other.value
            if isinstance(result, np.int64):
                return Int(result).set_context(self.context), None
            else:
                return Float(result).set_context(self.context), None
    
    def dived_by(self, other): 
        if isinstance(other, (Int, Float)):
            if repr(other) in ('0', '0.0'):
                return Float(np.inf).set_context(self.context), None
            else:
                result = self.value / other.value
                if isinstance(result, np.int64):
                    return Int(result).set_context(self.context), None
                else:
                    return Float(result).set_context(self.context), None

    def negated(self): 
        result = -self.value
        return Float(result).set_context(self.context), None


    def __repr__(self):
        return f'{self.value}'
        

#######################################
# OBJECTS
#######################################
object_object = Object()
null_object = Object(object_object)
int_object = Object(object_object)
float_object = Object(object_object)

#######################################
# CONTEXT
#######################################
class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None

#######################################
# SYMBOL TABLE
#######################################
class SymbolTable:
    def __init__(self, object):
        self.object = object

#######################################
# INTERPRETER
#######################################
class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        # "visit_BinOpNode"
        # "visit_NumberNode"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method found')

    def visit_NullNode(self, node, context):
        return RTResult().success(
            Null().set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_NumberNode(self, node, context):
        # print('found number node!')
        res = RTResult()
        if node.tok.type == TT_INT:
            return res.success(
                Int(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
            )
        else:
            return res.success(
                Float(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
            )   

    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.object.get(var_name)

        if not value:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f'"{var_name}" is not defined',
                context
            ))
        
        return res.success(value.set_context(context).set_pos(node.pos_start, node.pos_end))
     
    def visit_VarDeclareNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        old_value = context.symbol_table.object.slots.get(var_name, None)

        if old_value:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f'"{var_name}" is already defined',
                context
            ))
        
        value = res.register(self.visit(node.value_node, context))
        if res.error: return res

        context.symbol_table.object.set(var_name, value)
        return res.success(value)
          
    def visit_StatementsNode(self, node, context):
        res = RTResult() 
        lines = []
        for i in range(0, len(node.element_nodes)):
            line = res.register(self.visit(node.element_nodes[i], context))
            if res.error: return res
            lines.append(line)
        
        return res.success(lines[-1])


    
    def visit_BinOpNode(self, node, context):
        # print('found bin op node!')
        res = RTResult()

        left = res.register(self.visit(node.left_node, context))
        right = res.register(self.visit(node.right_node, context))
        if res.error: return res

        result = None
        error = None

        if node.op_tok.type == TT_PLUS:
            result, error  = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == TT_MUL:
            result, error = left.multed_by(right)
        elif node.op_tok.type == TT_DIV:
            result, error = left.dived_by(right)
        elif node.op_tok.type == TT_EQ:      
            if not isinstance(node.left_node, VarAccessNode):
                return res.failure(RTError(
                    node.left_node.pos_start, node.left_node.pos_end,
                    'Invalid left-hand side in assignment',
                    context
                ))

            var_name = node.left_node.var_name_tok.value

            value = res.register(self.visit(node.right_node, context))
            if res.error: return res

            context.symbol_table.object.set(var_name, value)
            return res.success(value)
            
        if error: return res.failure(error)
        return res.success(result.set_context(context).set_pos(node.pos_start, node.pos_end))
            

    def visit_UnaryOpNode(self, node, context):
        # print('found un op node!')
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res

        error = None

        if node.op_tok.type == TT_MINUS:
            number, error = number.negated()
        
        if error: return res.failure(error)
        return res.success(number.set_pos(node.pos_start, node.pos_end))



#######################################
# RUN
#######################################
global_symbol_table = SymbolTable(Object(object_object))
global_symbol_table.object.set('global', global_symbol_table.object)

global_symbol_table.object.set('Object', object_object)
global_symbol_table.object.set('Int', int_object)
global_symbol_table.object.set('Float', float_object)

def runstring(text, fn='<anonymous>'):
    # Generate tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    # Generate AST
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    # Run program
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)
    if result.error: return None, result.error

    return result.value, None