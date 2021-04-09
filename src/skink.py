#########################################
# IMPORTS
#########################################
import numpy as np
import math
import struct
import string
from strings_with_arrows import *

#########################################
# CONSTANTS
#########################################
DIGITS = '0123456789'
INT_LIMIT = 2**32
LONG_LIMIT = 2**64
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS+DIGITS
# def is_neg_zero(n):
#     return struct.pack('>d', n) == '\x80\x00\x00\x00\x00\x00\x00\x00'

def get(lst,n): 
        try:
                return lst[n]
        except IndexError:
                return None

#########################################
# ERRORS
#########################################
class Error:
        def __init__(self, pos_start, pos_end, error_name, details):
                self.pos_start = pos_start
                self.pos_end = pos_end
                self.error_name = error_name
                self.details = details

        def as_string(self):
                result = f'{self.error_name}: {self.details}\n'
                result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
                result += '\n\n'+string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
                return result

     
class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start,pos_end,'Illegal Character',details)

class ExpectedCharError(Error):
	def __init__(self, pos_start, pos_end, details):

		super().__init__(pos_start, pos_end, 'Expected Character', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start,pos_end,'Invalid Syntax',details)


class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start,pos_end,'Runtime Error',details)
        self.context = context
        
    def as_string(self):
        result  = self.generate_traceback()
        result += f'{self.error_name}: {self.details}'
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
                result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
                pos = ctx.parent_entry_pos
                ctx = ctx.parent

        return 'Traceback (most recent call last):\n' + result


class IncompatibleTypesError(RTError):
    def __init__(self, pos_start, pos_end, details,context):
        super().__init__(pos_start,pos_end,details,context)
        self.error_name = 'Incompatible Types'

#########################################
# POSITION
#########################################   
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

    def unadvance(self, current_char=None):
        self.idx -= 1
        self.col -= 1

        if current_char == '\n':
            self.ln -= 1
            self.col = 0

        return self


    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

#########################################
# TOKENS
#########################################
TT_INT = 'INT'
TT_LONG = 'LONG'
TT_DOUBLE = 'DOUBLE'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD = 'KEYWORD'
TT_EQ = 'EQ'
TT_EE = 'EE'
TT_LT = 'LT'
TT_LTE = 'LTE'
TT_GT = 'GT'
TT_GTE = 'GTE'
TT_NE = 'NE'
TT_LCURLY = 'LCURLY'
TT_RCURLY = 'RCURLY'
KEYWORDS = [
        'and',
        'or',
        'not',
        'if',
        'else'
]


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
    
    def matches(self, type_, value):
                return self.type == type_ and self.value == value
                
    def __repr__(self):
            if self.value: return f'{self.type}:{self.value}'
            return f'{self.type}'

#########################################
# LEXER
#########################################

class Lexer:
    def __init__(self,fn,text):
            self.fn = fn
            self.text = text
            self.pos = Position(-1,0,-1,fn,text)
            self.current_char = None
            self.advance()
    
    def advance(self):
            self.pos.advance(self.current_char)
            self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
    
    def unadvance(self):
            self.pos.unadvance(self.current_char)
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
                elif self.current_char == '{':
                        tokens.append(Token(TT_LCURLY, pos_start=self.pos))
                        self.advance()
                elif self.current_char == '}':
                        tokens.append(Token(TT_RCURLY, pos_start=self.pos))
                        self.advance()
                elif self.current_char == '!':
                        tok, error = self.make_not_equals()
                        if error: return [], error
                        tokens.append(tok)
                elif self.current_char == '=':
                        tokens.append(self.make_equals())
                        self.advance()
                elif self.current_char == '<':
                        tokens.append(self.make_less_than())
                        self.advance()
                elif self.current_char == '>':
                        tokens.append(self.make_greater_than())
                        self.advance()
                else:
                        pos_start = self.pos.copy()
                        char = self.current_char
                        self.advance()
                        return [], IllegalCharError(pos_start, self.pos, '"'+char+'"')

            tokens.append(Token(TT_EOF, pos_start=self.pos))
            return tokens, None
    
    def make_number(self):
            num_str = ''
            dot_count = 0
            pos_start = self.pos.copy()
            l_count = 0
            while self.current_char != None and self.current_char in DIGITS + '.Ll':
                if self.current_char == '.':
                        if dot_count == 1: break
                        dot_count += 1
                        num_str += '.'
                elif self.current_char in 'Ll':
                        if l_count == 1: break
                        l_count += 1
                else:
                        num_str += self.current_char
                self.advance()
            
            if dot_count == 0 and l_count == 0:
                    return Token(TT_INT, np.int32(math.fmod(float(num_str),INT_LIMIT)),pos_start,self.pos)
            elif l_count == 1:
                    return Token(TT_LONG, np.int64(math.fmod(float(num_str),INT_LIMIT)),pos_start,self.pos)
            else:
                    return Token(TT_DOUBLE, float(num_str), pos_start, self.pos)

    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
                id_str += self.current_char
                self.advance()

        tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos)
    
    def make_not_equals(self): 
            pos_start = self.pos.copy()
            self.advance()
            if self.current_char == '=':
                    self.advance()
                    return Token(TT_NE,pos_start=pos_start,pos_end=self.pos), None
            return None, ExpectedCharError(pos_start, self.pos, '"=" (after "!")')

    def make_equals(self):
                tok_type = TT_EQ
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '=':
                        self.advance()
                        tok_type = TT_EE

                self.unadvance()
                return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self):
                tok_type = TT_LT
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                        self.advance()
                        tok_type = TT_LTE

                self.unadvance()
                return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_greater_than(self):
                tok_type = TT_GT
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                        self.advance()
                        tok_type = TT_GTE

                self.unadvance()
                return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

#########################################
# NODES
#########################################
class NumberNode:
        def __init__(self,tok):
                self.tok = tok
                self.pos_start = self.tok.pos_start
                self.pos_end = self.tok.pos_end
        def __repr__(self):
                return f'{self.tok}'

class VarAccessNode:
	def __init__(self, var_name_tok):
		self.var_name_tok = var_name_tok

		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.var_name_tok.pos_end

class VarAssignNode:
        def __init__(self, var_name_tok, value_node, type_tok=None):
                self.var_name_tok = var_name_tok
                self.value_node = value_node
                self.type_tok = type_tok
                self.pos_start = self.type_tok.pos_start
                self.pos_end = self.value_node.pos_end

class SetNode:
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

                self.pos_start = self.left_node.pos_start
                self.pos_end = self.right_node.pos_end
        def __repr__(self):
                return f'({self.left_node},{self.op_tok},{self.right_node})'

class UnaryOpNode:
        def __init__(self, op_tok, node):
                self.op_tok = op_tok
                self.node = node
                self.pos_start = self.op_tok.pos_start
                self.pos_end = node.pos_end

        def __repr__(self):
                return f'({self.op_tok}, {self.node})'

#########################################
# PARSE RESULT
#########################################
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




#########################################
# PARSER
#########################################
class Parser:
        def __init__(self, tokens):
                self.tokens = tokens
                self.tok_idx = -1
                self.advance()

        def advance(self):
                self.tok_idx += 1
                if self.tok_idx < len(self.tokens):
                        self.current_tok = self.tokens[self.tok_idx]
                return self.current_tok
        
        def unadvance(self):
                self.tok_idx -= 1
                if self.tok_idx < len(self.tokens):
                        self.current_tok = self.tokens[self.tok_idx]
                return self.current_tok

        def parse(self):
                res = self.expr()
                if not res.error and self.current_tok.type != TT_EOF:
                        return res.failure(InvalidSyntaxError(
                                self.current_tok.pos_start, self.current_tok.pos_end,
                                'Expected "+", "-", "*" or "/"'
                        ))
                return res
                
        def if_expr(self):
                res = ParseResult()
                cases = []
                else_case = None

                if not self.current_tok.matches(TT_KEYWORD,'if'):
                        return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        'Expected "if"'
                        ))

                res.register(self.advance())
                condition = res.register(self.expr())
                if res.error: return res
                print(self.current_tok.type)
                if not self.current_tok.type == TT_LCURLY:
                        return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        'Expected "{"'
                        ))

                res.register(self.advance())
                res.register(self.advance())
                if not self.current_tok.type == TT_RCURLY:
                        return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        'Expected "}"'
                        ))

                while self.current_tok.matches(TT_KEYWORD, 'ELSE') and get(self.tokens,self.tok_idx+1).matches(TT_KEYWORD,'IF'):
                        res.register(self.advance())
                        res.register(self.advance())             

                        condition = res.register(self.expr())
                        if res.error: return res
                        if not self.current_tok.type == TT_LCURLY:
                                return res.failure(InvalidSyntaxError(
                                self.current_tok.pos_start, self.current_tok.pos_end,
                                f"Expected 'THEN'"
                                ))

        #########################################
        def factor(self): 
                res = ParseResult()
                tok = self.current_tok
                if tok.type in (TT_PLUS,TT_MINUS):
                        res.register(self.advance())
                        factor = res.register(self.factor())
                        if res.error: return res 
                        return res.success(UnaryOpNode(tok, factor))
                elif tok.type in (TT_INT,TT_LONG,TT_DOUBLE):
                        res.register(self.advance())
                        return res.success(NumberNode(tok))
                elif tok.type == TT_IDENTIFIER and getattr(get(self.tokens,self.tok_idx+1),"type",None) != TT_IDENTIFIER:
                        temp = res.success(VarAccessNode(tok))
                        res.register(self.advance())
                        return temp
                elif tok.matches(TT_KEYWORD,'if'):
                        if_expr = res.register(self.if_expr())
                        if res.error: return res
                        return res.success(if_expr)
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
                        "Expected int, long or double"
                ))

        def term(self): 
                return self.bin_op(self.factor, (TT_MUL,TT_DIV))

        def arith_expr(self):
                return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

        def comp_expr(self):
                res = ParseResult()

                if self.current_tok.matches(TT_KEYWORD, "not"):
                        op_tok = self.current_tok
                        res.register(self.advance())

                        node = res.register(self.comp_expr())
                        if res.error: return res
                        return res.success(UnaryOpNode(op_tok, node))

                node = res.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))

                if res.error:
                        return res.failure(InvalidSyntaxError(
                                self.current_tok.pos_start, self.current_tok.pos_end,
                                'Expected int, long, double, identifier, "+", "-", "(" or "not"'
                        ))

                return res.success(node)
        def expr(self): 
                res = ParseResult()
                temp = self.bin_op(self.comp_expr, ((TT_KEYWORD,"and"), (TT_KEYWORD,"or")))
                if(self.current_tok.type == TT_EQ):
                        res.register(self.unadvance())
                        var_name_tok = self.current_tok
                        res.register(self.advance())
                        if self.current_tok.type != TT_EQ:
                                return res.failure(InvalidSyntaxError(
                                        self.current_tok.pos_start, self.current_tok.pos_end,
                                        'Expected "="'
                                ))  
                        res.register(self.advance())
                        expr = res.register(self.expr())
                        if res.error: return res
                        return res.success(SetNode(var_name_tok,expr))

                if(self.current_tok.type == TT_IDENTIFIER 
                and get(self.tokens,self.tok_idx+1).type == TT_IDENTIFIER
                and get(self.tokens,self.tok_idx+2).type == TT_EQ):
                        type_node = self.current_tok
                        res.register(self.advance())
                        # if self.current_tok.type == TT_EOF:
                        #         res.register(self.unadvance())
                        #         return self.factor()
                        if self.current_tok.type != TT_IDENTIFIER:
                                return res.failure(InvalidSyntaxError(
                                        self.current_tok.pos_start, self.current_tok.pos_end,
                                        "Expected identifier"
                                ))

                        var_name = self.current_tok
                        res.register(self.advance())
                        if self.current_tok.type != TT_EQ:
                                return res.failure(InvalidSyntaxError(
                                        self.current_tok.pos_start, self.current_tok.pos_end,
                                        'Expected "="'
                                ))  
                        res.register(self.advance())
                        expr = res.register(self.expr())
                        if res.error: return res
                        
                        return res.success(VarAssignNode(var_name, expr, type_node)) 

                return temp
        def bin_op(self, func_a, ops, func_b=None):
                if func_b == None:
                        func_b = func_a

                res = ParseResult()
                left = res.register(func_a())
                if res.error: return res

                while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
                        op_tok = self.current_tok
                        res.register(self.advance())
                        right = res.register(func_b())
                        if res.error: return res
                        left = BinOpNode(left, op_tok, right)

                return res.success(left)


#########################################
# RUNTIME RESULT
#########################################
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
# SYMBOL TABLE
#######################################

class SymbolTable:
        def __init__(self):
                self.symbols = {}
                self.parent = None

        def get(self, name):
                # if self == global_symbol_table:
                #         # print(self.symbols,name,self.symbols.get(name,None))
                value = self.symbols.get(name, None)
                if value == None and self.parent:
                        return self.parent.get(name)
                return value

        def set(self, name, value):
                self.symbols[name] = value

        def remove(self, name):
                del self.symbols[name]

class NativeType(SymbolTable):
        def set_pos(self, pos_start=None, pos_end=None):
                self.pos_start = pos_start
                self.pos_end = pos_end
                return self
        def set_context(self, context=None):
                self.context = context
                return self


class Int(NativeType): 
        def __init__(self,value):
                super().__init__()
                self.set('value', np.int32(int(value)%INT_LIMIT))
                self.set_pos()
                self.set_context()

        def __add__(self,that):
                if isinstance(that,Double) or isinstance(that,Long):
                        return that+self
                if not isinstance(that,SymbolTable):
                        return RTError("")
                return Int(self.get('value')+that.get('value')).set_context(self.context), None
        def __sub__(self,that):
                if isinstance(that,Double) or isinstance(that,Long):
                        return -(that-self)
                return Int(self.get('value')-that.get('value')).set_context(self.context), None
        def __mul__(self,that):
                if isinstance(that,Double) or isinstance(that,Long):
                        return that*self
                return Int(self.get('value')*that.get('value')).set_context(self.context), None
        def __truediv__(self,that):
                if isinstance(that,Double) or isinstance(that,Long):
                        return type(that)(self)/(that)
                if isinstance(that,Int) and that.get('value') == 0:
                        return None, RTError(
                                that.pos_start, that.pos_end,
                                'Integer division by zero',
                                self.context
                        )

                return Int(self.get('value')/that.get('value')).set_context(self.context), None
        def __mod__(self,that):
                if isinstance(that,Double) or isinstance(that,Long):
                        return type(that)(self)%(that)
                return Int(self.get('value')%that.get('value')).set_context(self.context), None
        def __neg__(self):
                return Int(-self.get('value')), None
        def __lt__(self,that): 
                return Boolean(self.get('value')<that.get('value')), None
        def __le__(self,that): 
                return Boolean(self.get('value')<=that.get('value')), None
        def __gt__(self,that): 
                return Boolean(self.get('value')>that.get('value')), None
        def __ge__(self,that): 
                return Boolean(self.get('value')>=that.get('value')), None
        def equalTo(self,that): 
                return Boolean(self.get('value')==that.get('value')), None
        def __repr__(self):
                return self.get('value').__repr__()

class Long(NativeType): 
        def __init__(self,value):
                super().__init__()
                self.set('value', np.int64(math.fmod(float(value.__repr__()),LONG_LIMIT)))
                self.set_pos()
                self.set_context()

        def __add__(self,that):
                if isinstance(that,Double) or isinstance(that,Long):
                        return type(that)(self)+(that)
                return Long(self.get('value')+that.get('value')).set_context(self.context), None
        def __sub__(self,that):
                if isinstance(that,Double) or isinstance(that,Long):
                        return type(that)(self)-(that)
                return Long(self.get('value')-that.get('value')).set_context(self.context), None
        def __mul__(self,that):
                if isinstance(that,Double) or isinstance(that,Long):
                        return type(that)(self)*(that)
                return Long(self.get('value')*that.get('value')).set_context(self.context), None
        def __truediv__(self,that):
                if isinstance(that,Double):
                        return type(that)(self)/(that)
                if  that.get('value') == 0:
                        return None, RTError(
                                that.pos_start, that.pos_end,
                                'Integer division by zero',
                                self.context
                        )

                return Long(self.get('value')//that.get('value')).set_context(self.context), None
        def __mod__(self,that):
                if isinstance(that,Double) or isinstance(that,Long):
                        return type(that)(self)%(that)
                return Long(self.get('value')%that.get('value')).set_context(self.context), None
        def __neg__(self):
                return Long(-self.get('value')), None
        def __lt__(self,that): 
                return Boolean(self.get('value')<that.get('value')), None
        def __le__(self,that): 
                return Boolean(self.get('value')<=that.get('value')), None
        def __gt__(self,that): 
                return Boolean(self.get('value')>that.get('value')), None
        def __ge__(self,that): 
                return Boolean(self.get('value')>=that.get('value')), None
        def equalTo(self,that): 
                return Boolean(self.get('value')==that.get('value')), None
        def __repr__(self):
                return self.get('value').__repr__()

class Double(NativeType): 
        def __init__(self,value):
                super().__init__()
                self.set('value', float(value.__repr__()))
                self.set_pos()
                self.set_context()

        def __add__(self,that):
                return Double(self.get('value')+that.get('value')).set_context(self.context), None
        def __sub__(self,that):
                return Double(self.get('value')-that.get('value')).set_context(self.context), None
        def __mul__(self,that):
                return Double(self.get('value')*that.get('value')).set_context(self.context), None
        def __truediv__(self,that):
                if(math.copysign(1,that.get('value')) == -1.0 and that.get('value') == 0.0):
                        if(self.get('value') == 0.0):
                                return Double(math.nan).set_context(self.context), None
                        return Double(-math.inf).set_context(self.context), None
                if(that.get('value') == 0.0):
                        if(self.get('value') == 0.0):
                                return Double(math.nan).set_context(self.context), None
                        return Double(math.inf), None
                return Double(self.get('value')/that.get('value')).set_context(self.context), None
        def __mod__(self,that):
                return Double(self.get('value')%that.get('value')).set_context(self.context), None
        def __neg__(self):
                return Double(-(self.get('value'))), None
        def __lt__(self,that): 
                return Boolean(self.get('value')<that.get('value')), None
        def __le__(self,that): 
                return Boolean(self.get('value')<=that.get('value')), None
        def __gt__(self,that): 
                return Boolean(self.get('value')>that.get('value')), None
        def __ge__(self,that): 
                return Boolean(self.get('value')>=that.get('value')), None
        def equalTo(self,that): 
                return Boolean(self.get('value')==that.get('value')), None
        def __repr__(self):
                if self.get('value') == math.inf:
                        return "Infinity"
                if self.get('value') == -math.inf:
                        return "-Infinity"
                return self.get('value').__repr__()

class Boolean(NativeType): 
        def __init__(self,value):
                super().__init__()
                if isinstance(value,SymbolTable) and value.get('value') != None:
                        value = value.get('value')
                self.set('value', not not value)
                self.set_pos()
                self.set_context()
        def logicalAnd(self,that):
                return Boolean(self.get('value') and that.get('value'))
        def logicalOr(self,that):
                return Boolean(self.get('value') or that.get('value'))
        def logicalNot(self):
                return Boolean(not self.get('value'))
        def __bool__(self):
                return self.get('value')
        def __repr__(self):
                return self.get('value').__repr__().lower()
# print(Boolean(1))

#########################################
# CONTEXT
#########################################
class Context:
        def __init__(self, display_name, parent=None, parent_entry_pos=None):
                self.display_name = display_name
                self.parent = parent
                self.parent_entry_pos = parent_entry_pos
                self.symbol_table = None

#########################################
# INTERPRETER
#########################################
class Interpreter:
        def visit(self,node,context):
                method_name = f'visit_{type(node).__name__}'
                # "visit_BinOpNode"
                method = getattr(self, method_name, self.no_visit_method)
                return method(node,context)

        def no_visit_method(self, node, context):
                raise Exception(f'No visit_{type(node).__name__} method defined')

        def visit_NumberNode(self,node, context):
                res = RTResult()
                #print("Found number node!")
                if node.tok.type == TT_INT:
                        return res.success(
                                Int(node.tok.value).set_pos(node.tok.pos_start, node.tok.pos_end).set_context(context))
                elif node.tok.type == TT_LONG:
                        return res.success(
                                Long(node.tok.value).set_pos(node.tok.pos_start, node.tok.pos_end).set_context(context))
                else:
                        return res.success(
                                Double(node.tok.value).set_pos(node.tok.pos_start, node.tok.pos_end).set_context(context))

        def visit_VarAccessNode(self,node,context):
                res = RTResult()
                var_name = node.var_name_tok.value
                value = context.symbol_table.get(var_name)
                if value == None:
                        return res.failure(RTError(
                                node.pos_start, node.pos_end,
                                f'"{var_name}" is not defined.',
                                context
                        ))
                
                return res.success(value)
        def visit_VarAssignNode(self,node,context):
                res = RTResult()
                var_name = node.var_name_tok.value
                value = res.register(self.visit(node.value_node,context))
                theType = res.register(self.visit(VarAccessNode(node.type_tok),context))
                currentValue = context.symbol_table.get(var_name)
                if res.error: return res
                if not (theType == get_type(value)):
                        return res.failure(IncompatibleTypesError(
                                node.pos_start, node.pos_end,
                                f'{get_display_type(value)} cannot be converted to {node.type_tok.value}',
                                context
                        ))
                if currentValue != None and (not (get_type(currentValue) == get_type(value))):
                        return res.failure(IncompatibleTypesError(
                                node.pos_start, node.pos_end,
                                f'Identifier "{node.var_name_tok.value}" was previously declared with type {get_display_type(currentValue)}, but here has type {get_display_type(value)}.',
                                context
                        ))

                context.symbol_table.set(var_name,value)
                return res.success(value)

        def visit_SetNode(self,node,context):
                res = RTResult()
                var_name = node.var_name_tok.value
                currentValue = context.symbol_table.get(var_name)
                value = res.register(self.visit(node.value_node,context))
                if not currentValue:
                        return res.failure(RTError(
                                node.pos_start, node.pos_end,
                                f'"{var_name}" is not defined.',
                                context
                        ))

                if res.error: return res
                context.symbol_table.set(var_name,value)
                if not (get_type(currentValue) == get_type(value)):
                        return res.failure(IncompatibleTypesError(
                                node.pos_start, node.pos_end,
                                f'Identifier "{node.var_name_tok.value}" was previously declared with type {get_display_type(currentValue)}, but here has type {get_display_type(value)}.',
                                context
                        ))

                return res.success(value)
        def visit_BinOpNode(self,node,context):
                res = RTResult()
                result = None
                #print("Found bin op node!")
                left = res.register(self.visit(node.left_node,context))
                right = res.register(self.visit(node.right_node,context))
                if node.op_tok.type == TT_PLUS:
                        if((not getattr(left,"__add__",None)) or isinstance(left,type)):
                                return res.failure(RTError(
                                        node.pos_start, node.pos_end,
                                        f'binary operator "+" cannot be applied to operands of type {get_display_type(left)} and {get_display_type(right)}',
                                        context
                                ))
                        result, error = left+right
                elif node.op_tok.type == TT_MINUS:
                        if((not getattr(left,"__sub__",None)) or isinstance(left,type)):
                                return res.failure(RTError(
                                        node.pos_start, node.pos_end,
                                        f'binary operator "-" cannot be applied to operands of type {get_display_type(left)} and {get_display_type(right)}',
                                        context
                                ))
                        result, error = left-right
                elif node.op_tok.type == TT_MUL:
                        if((not getattr(left,"__mul__",None)) or isinstance(left,type)):
                                return res.failure(RTError(
                                        node.pos_start, node.pos_end,
                                        f'binary operator "*" cannot be applied to operands of type {get_display_type(left)} and {get_display_type(right)}',
                                        context
                                ))
                        result, error = left*right
                elif node.op_tok.type == TT_DIV:
                        if((not getattr(left,"__div__",None)) or isinstance(left,type)):
                                return res.failure(RTError(
                                        node.pos_start, node.pos_end,
                                        f'binary operator "/" cannot be applied to operands of type {get_display_type(left)} and {get_display_type(right)}',
                                        context
                                ))
                        result, error= left/right
                elif node.op_tok.type == TT_LT:
                        if((not getattr(left,"__lt__",None)) or isinstance(left,type)):
                                return res.failure(RTError(
                                        node.pos_start, node.pos_end,
                                        f'binary operator "<" cannot be applied to operands of type {get_display_type(left)} and {get_display_type(right)}',
                                        context
                                ))
                        result, error= left<right
                elif node.op_tok.type == TT_LTE:
                        if((not getattr(left,"__le__",None)) or isinstance(left,type)):
                                return res.failure(RTError(
                                        node.pos_start, node.pos_end,
                                        f'binary operator "<=" cannot be applied to operands of type {get_display_type(left)} and {get_display_type(right)}',
                                        context
                                ))
                        result, error= left<=right
                elif node.op_tok.type == TT_GT:
                        if((not getattr(left,"__gt__",None)) or isinstance(left,type)):
                                return res.failure(RTError(
                                        node.pos_start, node.pos_end,
                                        f'binary operator ">" cannot be applied to operands of type {get_display_type(left)} and {get_display_type(right)}',
                                        context
                                ))
                        result, error= left>right
                elif node.op_tok.type == TT_GT:
                        if((not getattr(left,"__ge__",None)) or isinstance(left,type)):
                                return res.failure(RTError(
                                        node.pos_start, node.pos_end,
                                        f'binary operator ">" cannot be applied to operands of type {get_display_type(left)} and {get_display_type(right)}',
                                        context
                                ))
                        result, error= left>=right
                elif node.op_tok.type == TT_GTE:
                        if((not getattr(left,"__ge__",None)) or isinstance(left,type)):
                                return res.failure(RTError(
                                        node.pos_start, node.pos_end,
                                        f'binary operator ">=" cannot be applied to operands of type {get_display_type(left)} and {get_display_type(right)}',
                                        context
                                ))
                        result, error= left>right
                elif node.op_tok.type == TT_EE:
                        result, error = Boolean(str(left) == str(right) and type(left) == type(right)), None
                elif node.op_tok.matches(TT_KEYWORD,'and'):
                        result, error = Boolean(left).logicalAnd(Boolean(right)), None
                elif node.op_tok.matches(TT_KEYWORD,'or'):
                        result, error = Boolean(left).logicalOr(Boolean(right)), None

                if error:
                        return res.failure(error)

                return res.success(result.set_pos(node.pos_start, node.pos_end))

        def visit_UnaryOpNode(self,node,context):
                res = RTResult()
                number = res.register(self.visit(node.node,context))
                error = None
                if res.error: return res
                
                if node.op_tok.type == TT_MINUS:
                        if((not getattr(number,"__neg__",None)) or isinstance(number,type)):
                                return res.failure(RTError(
                                        node.pos_start, node.pos_end,
                                        f'unary operator "-" cannot be applied to an operand of type {get_display_type(number)}',
                                        context
                                ))
                        number, error = -number
                elif node.op_tok.matches(TT_KEYWORD,'not'):
                        # if((not getattr(number,"logicalNot",None)) or isinstance(number,type)):
                        #         return res.failure(RTError(
                        #                 node.pos_start, node.pos_end,
                        #                 f'unary operator "not" cannot be applied to an operand of type {get_display_type(number)}',
                        #                 context
                        #         ))
                        number, error = Boolean(number).logicalNot(), None
                if error:
                        return res.failure(error)
                else:
                        return res.success(number)
                
        
#######################################
# TYPES
#######################################
def get_type(n):
        if isinstance(n,type):
                return global_symbol_table.get('type')
        if isinstance(n,Int):
                return Int
        elif isinstance(n,Long):
                return Long
        elif isinstance(n,Double):
                return Double
        elif isinstance(n,Boolean):
                return Boolean
        else:
                raise Exception(f'No type found for {n}')

def display_name(theType):
        if theType == Int:
                return "int"
        elif theType == Long:
                return "long"
        elif theType == Double:
                return "double"
        elif theType == Boolean:
                return "boolean"
        elif theType == global_symbol_table.get('type'):
                return "type"
        else:
                return str(theType)

def get_display_type(n):
       return display_name(get_type(n))

def prettyPrint(n):
        if n == None:
                return "None"
        elif isinstance(n,type):
                return f'[Class: {display_name(n)}]'
        elif (not "0x" in n.__repr__()):
                return n.__repr__()
        else:
                return str(n)
#########################################
# RUN
#########################################
global_symbol_table = SymbolTable()
global_symbol_table.set('true',Boolean(True))
global_symbol_table.set('false',Boolean(False))
global_symbol_table.set('int',Int)
global_symbol_table.set('long',Long)
global_symbol_table.set('double',Double)
global_symbol_table.set('boolean',Boolean)
global_symbol_table.set('type',lambda:None)
# print(global_symbol_table.get('false'))
def run(fn,text):
        # Generate tokens
        lexer = Lexer(fn,text)
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
