# Skink source code
# Usage permitted under terms of MIT License

#######################################
# IMPORTS
#######################################
import numpy as np
import string
import uuid
import math

#######################################
# CONSTANTS
#######################################
DIGITS = '0123456789'
LETTERS = string.ascii_letters + '$_'
LETTERS_DIGITS = LETTERS + DIGITS
I32_MIN_VALUE = -2147483648
I32_MAX_VALUE = 2147483647
I64_MIN_VALUE = -9223372036854775808
I64_MAX_VALUE = 9223372036854775807

#######################################
# UTILITY FUNCTIONS
#######################################
def instanceof(a, b):
    return a.type.uuid == b.uuid

#######################################
# ERRORS
#######################################
class LangError:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += f'\nFile {self.pos_start.fn}, line {self.pos_start.ln+1}'
        return result

class IllegalCharError(LangError):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)


class InvalidSyntaxError(LangError):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)


class RTError(LangError):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'Runtime Error', details)
        self.context = context

    def as_string(self):
        result = self.generate_traceback()
        result += f'{self.error_name}: {self.details}'
        # result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

    def generate_traceback(self):
        if not self.context: return ''
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return 'Traceback (most recent call last):\n' + result


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

		def advance(self, current_char=None):
				self.idx += 1
				self.col += 1

				if current_char == '\n':
						self.ln += 1
						self.col = 0

				return self

		def copy(self):
				return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


#######################################
# TOKENS
#######################################
TT_INT		= 'INT'
TT_LONG     = 'LONG'
TT_FLOAT    = 'FLOAT'
TT_DOUBLE   = 'DOUBLE'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'
TT_EQ       = 'EQ'
TT_KEYWORD  = 'KEYWORD'
TT_IDENTIFIER = 'IDENTIFIER'
TT_EOF      = 'EOF'
KEYWORDS = []

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
    
    def errorText(self):
        # print(self.pos_start.idx)
        # print(self.pos_end.idx)        
        return self.pos_start.ftxt[self.pos_start.idx-1:self.pos_end.idx-1]

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
        self.pos.advance()
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
            elif self.current_char == '=':
                tokens.append(Token(TT_EQ, pos_start=self.pos))
                self.advance()
            else:
                # return some error
                char = self.current_char
                pos_start = self.pos.copy()
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, f'"{char}"')
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, []


    def make_number(self):
        pos_start = self.pos.copy()

        num_str = ''
        l_count = 0
        f_count = 0
        dot_count = 0

        while self.current_char != None and self.current_char in (DIGITS + 'LlFf.'):
            if self.current_char in 'Ll':
                if l_count == 1: break # there are no "long long"s yet
                l_count += 1
            elif self.current_char in 'Ff':
                if f_count == 1: break
                f_count += 1
            elif self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
        
        if f_count == 1: # float
            return Token(TT_FLOAT, np.float32(num_str), pos_start=pos_start, pos_end=self.pos)
        if dot_count == 1: # double
            return Token(TT_DOUBLE, float(num_str), pos_start=pos_start, pos_end=self.pos )
        elif l_count == 1: # long
            clipped_num = np.clip(int(num_str), I64_MIN_VALUE, I64_MAX_VALUE)
            return Token(TT_LONG, np.int64(clipped_num), pos_start=pos_start, pos_end=self.pos)
        else: # int
            clipped_num = np.clip(int(num_str), I32_MIN_VALUE, I32_MAX_VALUE)
            return Token(TT_INT, np.int32(clipped_num), pos_start=pos_start, pos_end=self.pos )
    
    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()

        tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos)



#######################################
# NODES
#######################################
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

class VarDefineNode:
    def __init__(self, type_node, var_name_tok, value_node):
        self.type_node = type_node
        self.var_name_tok = var_name_tok
        self.value_node = value_node

        self.pos_start = self.type_node.pos_start
        self.pos_end = self.value_node.pos_end

class VarSetNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.value_node.pos_end

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

        self.pos_start = self.op_tok.pos_start
        self.pos_end = self.node.pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'

#######################################
# PARSE RESULT
#######################################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node

        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
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

    def advance(self, ):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF:
            self.advance()
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f'Unexpected token "{self.current_tok.errorText()}"'
            ))
        return res

    ###################################

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register(self.advance())
            atom = res.register(self.atom())
            if res.error: return res
            return res.success(UnaryOpNode(tok, atom))
        
        elif tok.type in (TT_INT, TT_LONG, TT_FLOAT, TT_DOUBLE):
            res.register(self.advance())
            return res.success(NumberNode(tok))

        elif tok.type == TT_IDENTIFIER:
            res.register(self.advance())
            return res.success(VarAccessNode(tok))

        elif tok.type == TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    'Expected ")"'
                ))

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            f'Unexpected token "{tok.errorText()}"'
        ))

    def term(self):
        return self.bin_op(self.atom, (TT_MUL, TT_DIV))

    def expr(self):
        res = ParseResult()
        result = res.register(self.bin_op(self.term, (TT_PLUS, TT_MINUS)))
        if res.error: return res
        # self.advance()
        # print(self.current_tok.type)
        if self.current_tok.type == TT_IDENTIFIER:
            var_name_tok = self.current_tok
            self.advance()
            if self.current_tok.type != TT_EQ:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    'Expected "="'
                ))
            else:
                self.advance()
                value = res.register(self.expr())
                if res.error: return res
                return res.success(VarDefineNode(result, var_name_tok, value))
        else:
            return res.success(result)

            
        

    ###################################

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error: return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)


#######################################
# VALUES
#######################################
class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()
        self.set_type()
        self.uuid = uuid.uuid4()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def set_type(self, type_=None):
        if type_: type_.members.add(self)
        self.type = type_
        return self

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        return None, self.illegal_operation(other)

    def multed_by(self, other):
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        return None, self.illegal_operation(other)

    def powed_by(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_ne(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lte(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gte(self, other):
        return None, self.illegal_operation(other)

    def anded_by(self, other):
        return None, self.illegal_operation(other)

    def ored_by(self, other):
        return None, self.illegal_operation(other)

    def notted(self):
        return None, self.illegal_operation(self)

    def negated(self):
        return None, self.illegal_operation(self)

    def execute(self, args):
        return RTResult().failure(self.illegal_operation())

    def copy(self):
        raise Exception('No copy method defined')

    def is_true(self):
        return False

    def illegal_operation(self, other=None):
        if not other: other = self
        # print(self.pos_start)
        return RTError(
            self.pos_start, other.pos_end,
            'Illegal operation',
            self.context
        )

class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        if isinstance(self.value, np.int32):
            # int_type.members.add(self)
            self.set_type(int_type)
        elif isinstance(self.value, np.int64):
            # long_type.members.add(self)
            self.set_type(long_type)
        elif isinstance(self.value, np.float32):
            # float_type.members.add(self)
            self.set_type(float_type)
        elif isinstance(self.value, float):
            # double_type.members.add(self)
            self.set_type(double_type)

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def dived_by(self, other):
        if isinstance(other, Number):
            if repr(other.value) == '0':
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Attempt to divide by zero',
                    self.context
                )
            elif repr(other.value) == '0.0':
                return Number(math.inf).set_context(self.context), None


            if isinstance(self.value, (np.int32, np.int64)) and isinstance(other.value, (np.int32, np.int64)):
                return Number(self.value // other.value).set_context(self.context), None
            
            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    # def powed_by(self, other):
    #     if isinstance(other, Number):
    #         return Number(np.power(self.value, other.value)).set_context(self.context), None
    #     else:
    #         return None, Value.illegal_operation(self, other)

    # def get_comparison_eq(self, other):
    #     if isinstance(other, Number):
    #         return Number(int(self.value == other.value)).set_context(self.context), None
    #     else:
    #         return None, Value.illegal_operation(self, other)

    # def get_comparison_ne(self, other):
    #     if isinstance(other, Number):
    #         return Number(int(self.value != other.value)).set_context(self.context), None
    #     else:
    #         return None, Value.illegal_operation(self, other)

    # def get_comparison_lt(self, other):
    #     if isinstance(other, Number):
    #         return Number(int(self.value < other.value)).set_context(self.context), None
    #     else:
    #         return None, Value.illegal_operation(self, other)

    # def get_comparison_gt(self, other):
    #     if isinstance(other, Number):
    #         return Number(int(self.value > other.value)).set_context(self.context), None
    #     else:
    #         return None, Value.illegal_operation(self, other)

    # def get_comparison_lte(self, other):
    #     if isinstance(other, Number):
    #         return Number(int(self.value <= other.value)).set_context(self.context), None
    #     else:
    #         return None, Value.illegal_operation(self, other)

    # def get_comparison_gte(self, other):
    #     if isinstance(other, Number):
    #         return Number(int(self.value >= other.value)).set_context(self.context), None
    #     else:
    #         return None, Value.illegal_operation(self, other)

    # def anded_by(self, other):
    #     if isinstance(other, Number):
    #         return Number(int(self.value and other.value)).set_context(self.context), None
    #     else:
    #         return None, Value.illegal_operation(self, other)

    # def ored_by(self, other):
    #     if isinstance(other, Number):
    #         return Number(int(self.value or other.value)).set_context(self.context), None
    #     else:
    #         return None, Value.illegal_operation(self, other)

    # def notted(self):
    #     return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def negated(self):
        return Number(-self.value).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0

    def __repr__(self):
        return str(self.value)

class Type(Value):
    def __init__(self, name='<anonymous>', add_to_type_type=True):
        super().__init__()
        self.name = name
        self.members = set()
        if add_to_type_type: self.set_type(type_type)
    
    def __repr__(self):
        return f'<type "{self.name}">'

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
# CONTEXT
#######################################

class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None, symbol_table=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = symbol_table
    

#######################################
# SYMBOL TABLE
#######################################

class SymbolTable:
    def __init__(self, parent=None):
        self.parent = parent
        self.symbols = {}
        self.types = {}
    
    def get(self, name, context):
        key = str(name)
        value = self.symbols.get(key, None)
        if value == None and self.parent:
            return self.parent.get(name)
        else:
            return value

    def define(self, type_, name, value, context=None):
        key = str(name)
        if key in self.symbols:
            return None, RTError(
                value.pos_start, value.pos_end,
                f'"{key}" is already defined',
                context
            )
        else:
            if instanceof(value, type_):
                self.symbols[key] = value
                return value, None   
            else:
                return None, RTError(
                    value.pos_start, value.pos_end,
                    f'"{value.type.name}" cannot be converted to "{type_.name}"',
                    context
                )

    def set(self, name, value, context=None):
        key = str(name)
        if key in self.symbols:
            old_value = self.get(key, context) 
            if instanceof(value, old_value.type):
                self.symbols[key] = value
                return value, None   
            else:
                return None, RTError(
                    value.pos_start, value.pos_end,
                    f'"{value.type.name}" cannot be converted to "{old_value.type.name}"',
                    context
                )
        else:
            self.symbols[key] = value
            return value, None


#######################################
# TYPES
#######################################
type_type = Type('type', False)
type_type.set_type(type_type)

int_type = Type('int')
long_type = Type('long')
float_type = Type('float')
double_type = Type('double')

#######################################
# INTERPRETER
#######################################
class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    #######################################

    def visit_NumberNode(self, node, context):
        # print('Found number node!')
        return RTResult().success(
            Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value

        value = context.symbol_table.get(var_name, context)
        if value == None:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f'"{var_name}" is not defined',
                context
            ))

        return res.success(value.set_pos(node.pos_start, node.pos_end).set_context(context))


    def visit_VarDefineNode(self, node, context):
        res = RTResult()
        type_ = res.register(self.visit(node.type_node, context))
        if res.error: return res

        var_name = node.var_name_tok.value

        value = res.register(self.visit(node.value_node, context))
        if res.error: return res
        
        result, error = context.symbol_table.define(type_, var_name, value, context)
        if error: return res.failure(error)

        return res.success(result)

    def visit_BinOpNode(self, node, context):
        # print('Found bin op node!')  
        res = RTResult()

        left = res.register(self.visit(node.left_node, context))
        if res.error: return res

        right = res.register(self.visit(node.right_node, context))
        if res.error: return res
        
        result = None
        error = None

        if node.op_tok.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == TT_MUL:
            result, error = left.multed_by(right)
        elif node.op_tok.type == TT_DIV:
            result, error = left.dived_by(right) 
        # elif node.op_tok.type == TT_POW:
        #     result, error = left.powed_by(right) 
        
        if error: 
            return res.failure(error)
        else:           
            return res.success(result.set_pos(node.pos_start, node.pos_end))
                      

    def visit_UnaryOpNode(self, node, context):
        # print('Found un op node!')
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res

        error = None
        if node.op_tok.type == TT_MINUS:
            number, error = number.negated()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))          

    

#######################################
# RUN
#######################################
global_symbol_table = SymbolTable()
global_symbol_table.define(type_type, 'type', type_type)
global_symbol_table.define(type_type, 'int', int_type)
global_symbol_table.define(type_type, 'long', long_type)
global_symbol_table.define(type_type, 'float', float_type)
global_symbol_table.define(type_type, 'double', double_type)

def run_text(fn, text):
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

    return result.value, result.error
