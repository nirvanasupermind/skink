# Skink source code
# Usage permitted under terms of MIT License

#######################################
# IMPORTS
#######################################
import numpy as np 
import uuid
import string
import sys

#######################################
# CONSTANTS
#######################################
DIGITS = '0123456789'
LETTERS = string.ascii_letters + '_'
LETTERS_DIGITS = LETTERS + DIGITS
BS = DIGITS + string.ascii_lowercase
NEWLINES = '\n\r'
DEFAULT_MAX_DEPTH = 500

I64_MIN_VALUE = -9223372036854775808
I64_MAX_VALUE = 9223372036854775807
FLOAT_MIN_VALUE = sys.float_info.min * sys.float_info.epsilon
FLOAT_MAX_VALUE = sys.float_info.max


#######################################
# UTILITY FUNCTIONS
#######################################

def to_skink_number(n):
    if isinstance(n, np.int64): return Int(n)
    return Float(n)

# taken from https://stackoverflow.com/questions/2267362/how-to-convert-an-integer-to-a-string-in-any-base
def to_base(s, b):
    res = ""
    while s:
        res+=BS[s%b]
        s//= b
    return res[::-1] or "0"

# taken from https://stackoverflow.com/questions/25488148/what-is-the-python-equivalent-of-javascripts-array-prototype-some
def some(list_, pred):
    return any(pred(i) for i in list_) #booleanize the values, and pass them to any

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
        result  += f'error: {self.details}'
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
        result  += f'error: {self.details}\n'
        result  += 'stack traceback: '
        result  += self.generate_traceback()
        return result

    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            if ctx.should_display:
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
TT_STRING   = 'STRING'
TT_KEYWORD  = 'KEYWORD'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_EQ       = 'EQ'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'
TT_LSQUARE  = 'LSQUARE'
TT_RSQUARE  = 'RSQUARE'
TT_LCURLY   = 'LCURLY'
TT_RCURLY   = 'RCURLY'
TT_COMMA    = 'COMMA'
TT_DOT      = 'DOT'
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
TT_BITAND   = 'BITAND'
TT_BITOR    = 'BITOR'
TT_BITXOR   = 'BITXOR'
TT_BITNOT   = 'BITNOT'
TT_PLUSEQ   = 'PLUSEQ'
TT_MINUSEQ  = 'MINUSEQ'
TT_MULEQ    = 'MULEQ'
TT_DIVEQ    = 'DIVEQ'
TT_BITANDEQ = 'BITANDEQ'
TT_BITOREQ  = 'BITOREQ'
TT_BITXOREQ = 'BITXOREQ'
TT_NEWLINE  = 'NEWLINE'
TT_EOF      = 'EOF'
KEYWORDS = [
    'nil',
    'true',
    'false',
    'var',
    'if',
    'else',
    'for',
    'while',
    'function',
    'return',
    'is'
]

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()

        if not pos_end and pos_start:
            self.pos_end = pos_start.copy()
            self.pos_end.advance(None)
        else:
            self.pos_end = pos_end

    def get_error_message(self):
        if self.type == TT_EOF: return 'unexpected end of input'
        return f'unexpected "{self.pos_start.ftxt[self.pos_start.idx:self.pos_end.idx]}"'
        
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
            elif self.current_char == '"':
                tok, error = self.make_string()
                if error: return [], None
                tokens.append(tok)
            elif self.current_char == '+':
                tokens.append(self.make_plus())
                # self.advance()
            elif self.current_char == '-':
                tokens.append(self.make_minus())
            elif self.current_char == '*':
                tokens.append(self.make_mul())
            elif self.current_char == '/':
                tok = self.make_div()
                if tok: tokens.append(tok)
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos.copy()))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos.copy()))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(TT_LSQUARE, pos_start=self.pos.copy()))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(TT_RSQUARE, pos_start=self.pos.copy()))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token(TT_LCURLY, pos_start=self.pos.copy()))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(TT_RCURLY, pos_start=self.pos.copy()))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA, pos_start=self.pos.copy()))
                self.advance()
            elif self.current_char == '.':
                tokens.append(Token(TT_DOT, pos_start=self.pos.copy()))
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
                tokens.append(Token(TT_BITNOT, pos_start=self.pos.copy()))
                self.advance()
            elif self.current_char in NEWLINES + ';':
                tokens.append(Token(TT_NEWLINE, pos_start=self.pos.copy()))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, f'illegal character "{char}"')

        tokens.append(Token(TT_EOF, pos_start=self.pos.copy()))
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
            clipped = np.clip(int(num_str), I64_MIN_VALUE, I64_MAX_VALUE)
            return Token(TT_INT, np.int64(clipped), pos_start, self.pos.copy())
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos.copy())

    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS:
            id_str += self.current_char
            self.advance()

        tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos.copy())

    def make_string(self):
        string = ''
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()
        
        escape_characters = {
            't': '\u0009',
            'b': '\u0008',
            'n': '\u000a',
            'r': '\u000d',
            'f': '\u000c',
            '"': '"',
            '\\': '\\\\'
        }

        while self.current_char != '"' or escape_character:
            if self.current_char == None:
                return None, InvalidSyntaxError(pos_start, self.pos.copy(), 'unclosed string literal')
            if escape_character:
                string += escape_characters.get(self.current_char, self.current_char)
                escape_character = False
            else:
                if self.current_char == '\\':
                    escape_character = True
                else:
                    string += self.current_char
            self.advance()
            
        self.advance()
        return Token(TT_STRING, string, pos_start, self.pos.copy()), None

    def make_plus(self):
        tok_type = TT_PLUS
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_PLUSEQ

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def make_minus(self):
        tok_type = TT_MINUS
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_MINUSEQ

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def make_mul(self):
        tok_type = TT_MUL
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_MULEQ

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def make_div(self):
        tok_type = TT_DIV
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '/':
            self.advance()
            while self.current_char != None and not self.current_char in NEWLINES:
                self.advance()
            
            self.advance()
            return


        if self.current_char == '=':
            self.advance()
            tok_type = TT_DIVEQ


        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def make_not_equals(self):
        tok_type = TT_NOT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_NE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())
        

    def make_equals(self):
        tok_type = TT_EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_EE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def make_less_than(self):
        tok_type = TT_LT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_LTE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def make_greater_than(self):
        tok_type = TT_GT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_GTE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def make_and(self):
        tok_type = TT_BITAND
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '&':
            self.advance()
            tok_type = TT_AND
        elif self.current_char == '=':
            self.advance()
            tok_type = TT_BITANDEQ

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def make_or(self):
        tok_type = TT_BITOR
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '|':
            self.advance()
            tok_type = TT_OR
        elif self.current_char == '=':
            self.advance()
            tok_type = TT_BITOREQ

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def make_xor(self):
        tok_type = TT_BITXOR
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '^':
            self.advance()
            tok_type = TT_XOR
        elif self.current_char == '=':
            self.advance()
            tok_type = TT_BITXOREQ

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    
#######################################
# NODES
#######################################
class NilNode:
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

class BoolNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end
    
    def __repr__(self):
        return f'{self.tok}'

class StringNode:
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

class VarAssignNode:
	def __init__(self, var_name_tok, value_node):
		self.var_name_tok = var_name_tok
		self.value_node = value_node

		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.value_node.pos_end

class ListNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes

        self.pos_start = pos_start
        self.pos_end = pos_end

class TupleNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes

        self.pos_start = pos_start
        self.pos_end = pos_end
        
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

class IfNode:
    def __init__(self, condition, if_case):
        self.condition = condition
        self.if_case = if_case

        self.pos_start = self.condition.pos_start
        self.pos_end = self.if_case.pos_end

class IfElseNode:
    def __init__(self, condition, if_case, else_case):
        self.condition = condition
        self.if_case = if_case
        self.else_case = else_case

        self.pos_start = self.condition.pos_start
        self.pos_end = self.else_case.pos_end


class ForNode:
    def __init__(self, statement1_node, statement2_node, statement3_node, body_node):
        self.statement1_node = statement1_node
        self.statement2_node = statement2_node
        self.statement3_node = statement3_node
        self.body_node = body_node

        self.pos_start = self.statement1_node.pos_start
        self.pos_end = self.body_node.pos_end


class WhileNode:
	def __init__(self, condition_node, body_node):
		self.condition_node = condition_node
		self.body_node = body_node

		self.pos_start = self.condition_node.pos_start
		self.pos_end = self.body_node.pos_end

class FuncDefNode:
	def __init__(self, var_name_tok, arg_name_toks, body_node):
		self.var_name_tok = var_name_tok
		self.arg_name_toks = arg_name_toks
		self.body_node = body_node

		if self.var_name_tok:
			self.pos_start = self.var_name_tok.pos_start
		elif len(self.arg_name_toks) > 0:
			self.pos_start = self.arg_name_toks[0].pos_start
		else:
			self.pos_start = self.body_node.pos_start

		self.pos_end = self.body_node.pos_end

class CallNode:
	def __init__(self, node_to_call, arg_nodes):
		self.node_to_call = node_to_call
		self.arg_nodes = arg_nodes

		self.pos_start = self.node_to_call.pos_start

		if len(self.arg_nodes) > 0:
			self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
		else:
			self.pos_end = self.node_to_call.pos_end

class DotNotationNode:
    def __init__(self, obj_node, prop_tok):
        self.obj_node = obj_node
        self.prop_tok = prop_tok
        
        self.pos_start = self.obj_node.pos_start
        self.pos_end = self.prop_tok.pos_end

class BracketNotationNode:
    def __init__(self, obj_node, prop_node):
        self.obj_node = obj_node
        self.prop_node = prop_node
        
        self.pos_start = self.obj_node.pos_start
        self.pos_end = self.prop_node.pos_end


class ReturnNode:
  def __init__(self, node_to_return, pos_start, pos_end):
    self.node_to_return = node_to_return

    self.pos_start = pos_start
    self.pos_end = pos_end

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
                self.current_tok.get_error_message()
            ))
        return res

    ###################################

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS, TT_NOT, TT_BITNOT):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))
        
        elif tok.matches(TT_KEYWORD, 'nil'):
            res.register_advancement()
            self.advance()
            return res.success(NilNode(tok))

        elif tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.matches(TT_KEYWORD, 'true') or tok.matches(TT_KEYWORD, 'false'):
            res.register_advancement()
            self.advance()
            return res.success(BoolNode(tok))

        elif tok.type == TT_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))

        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.type == TT_LPAREN:
            pos_start = self.current_tok.pos_start.copy()
            res.register_advancement()
            self.advance()

            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()   
                return res.success(TupleNode([], pos_start, self.current_tok.pos_end.copy()))           
            
                
            expr = res.register(self.expr())
            if res.error: return res

            if self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()
                if self.current_tok.type == TT_RPAREN:
                    res.register_advancement()
                    self.advance()
                    return res.success(TupleNode([expr], pos_start, self.current_tok.pos_end.copy()))
                else:
                    element_nodes = [expr]
                    self.reverse()            

                    while self.current_tok.type == TT_COMMA:
                        res.register_advancement()
                        self.advance()

                        element_nodes.append(res.register(self.expr()))
                        if res.error: return res

                    if self.current_tok.type != TT_RPAREN:
                        return res.failure(InvalidSyntaxError(
                            self.current_tok.pos_start, self.current_tok.pos_end,
                            self.current_tok.get_error_message()
                        ))

                    res.register_advancement()
                    self.advance()
                    return res.success(TupleNode(element_nodes, pos_start, self.current_tok.pos_end.copy()))

            elif self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    self.current_tok.get_error_message()
                ))

        elif self.current_tok.matches(TT_KEYWORD, 'if'):
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)
        elif self.current_tok.matches(TT_KEYWORD, 'for'):
            for_expr = res.register(self.for_expr())
            if res.error: return res
            return res.success(for_expr)
        elif self.current_tok.matches(TT_KEYWORD, 'while'):
            while_expr = res.register(self.while_expr())
            if res.error: return res
            return res.success(while_expr)
        elif self.current_tok.matches(TT_KEYWORD, 'function'):
            func_def = res.register(self.func_def())
            if res.error: return res
            
            return res.success(func_def)

        elif self.current_tok.type == TT_LSQUARE:
            list_expr = res.register(self.list_expr())
            if res.error: return res
            
            return res.success(list_expr)


        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            self.current_tok.get_error_message()
        ))

    def if_expr(self):
        res = ParseResult()
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                self.current_tok.get_error_message()
            ))

        condition = res.register(self.expr())
        if res.error: return res

        self.reverse()
        if self.current_tok.type != TT_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                self.current_tok.get_error_message()
            ))

        res.register_advancement()
        self.advance()

        body = res.register(self.curly_expr())
        if res.error: return res

        if self.current_tok.matches(TT_KEYWORD, 'else'): 
                res.register_advancement()
                self.advance()

                else_case = res.register(self.curly_expr())
                if res.error: return res

                return res.success(IfElseNode(condition, body, else_case))
        else: 
                return res.success(IfNode(condition, body))            

    def for_expr(self):
        res = ParseResult()
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                self.current_tok.get_error_message()
            ))


        res.register_advancement()
        self.advance()

        statement1 = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type != TT_NEWLINE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                self.current_tok.get_error_message()
            ))

        res.register_advancement()
        self.advance()

        statement2 = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type != TT_NEWLINE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                self.current_tok.get_error_message()
            ))

        res.register_advancement()
        self.advance()

        statement3 = res.register(self.expr())
        if res.error: return res
        if self.current_tok.type != TT_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                self.current_tok.get_error_message()
            ))

        res.register_advancement()
        self.advance()
        if self.current_tok.type != TT_LCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                self.current_tok.get_error_message()
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_RCURLY:
            tok = self.current_tok
            res.register_advancement()
            self.advance()

            statements = NilNode(tok)
        else:
            statements = res.register(self.statements())
            if res.error: return res
            
            if self.current_tok.type != TT_RCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    self.current_tok.get_error_message()
                ))
            
            res.register_advancement()
            self.advance()

        return res.success(ForNode(
            statement1,
            statement2,
            statement3,
            statements
        ))      

    def while_expr(self):
        res = ParseResult()
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                self.current_tok.get_error_message()
            ))

        condition = res.register(self.expr())
        if res.error: return res

        self.reverse()
        if self.current_tok.type != TT_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                self.current_tok.get_error_message()
            ))

        res.register_advancement()
        self.advance()
        if self.current_tok.type != TT_LCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                self.current_tok.get_error_message()
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_RCURLY:
            tok = self.current_tok
            res.register_advancement()
            self.advance()

            statements = NilNode(tok)
        else:
            statements = res.register(self.statements())

            if res.error: return res
            if self.current_tok.type != TT_RCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    self.current_tok.get_error_message()
                ))

            res.register_advancement()
            self.advance()

        return res.success(WhileNode(condition, statements))

    def func_def(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'function'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                self.current_tok.get_error_message()
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()
            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    self.current_tok.get_error_message()
                ))
        else:
            var_name_tok = None
            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    self.current_tok.get_error_message()
                ))
        
        res.register_advancement()
        self.advance()
        arg_name_toks = []

        if self.current_tok.type == TT_IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()
            
            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()

                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected identifier"
                    ))

                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()
            
            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected ',' or ')'"
                ))
        else:
            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected identifier or ')'"
                ))

        res.register_advancement()
        self.advance()

        body = res.register(self.curly_expr())
        if res.error: return res

        return res.success(FuncDefNode(
            var_name_tok,
            arg_name_toks,
            body
        ))

    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != TT_LSQUARE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '['"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_RSQUARE:
            res.register_advancement()
            self.advance()
        else:
            element_nodes.append(res.register(self.expr()))
            if res.error: return res

            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()

                element_nodes.append(res.register(self.expr()))
                if res.error: return res

            if self.current_tok.type != TT_RSQUARE:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    self.current_tok.get_error_message()
                ))

            res.register_advancement()
            self.advance()

        return res.success(ListNode(
        element_nodes,
        pos_start,
        self.current_tok.pos_end.copy()
        ))
        


    def call(self):
        res = ParseResult()
        factor = res.register(self.factor())
        if res.error: return res

        while self.current_tok.type in (TT_LPAREN, TT_DOT, TT_LSQUARE):
            if self.current_tok.type == TT_LPAREN:
                res.register_advancement()
                self.advance()
                arg_nodes = []

                if self.current_tok.type == TT_RPAREN:
                    res.register_advancement()
                    self.advance()
                else:
                    arg_nodes.append(res.register(self.expr()))
                    if res.error:
                        return res.failure(InvalidSyntaxError(
                            self.current_tok.pos_start, self.current_tok.pos_end,
                            self.current_tok.get_error_message()
                        ))

                    while self.current_tok.type == TT_COMMA:
                        res.register_advancement()
                        self.advance()

                        arg_nodes.append(res.register(self.expr()))
                        if res.error: return res

                        # res.register_advancement()
                        # self.advance()
                    
                    
                    # self.reverse()

                    if self.current_tok.type != TT_RPAREN:
                        return res.failure(InvalidSyntaxError(
                            self.current_tok.pos_start, self.current_tok.pos_end,
                            self.current_tok.get_error_message()
                        ))

                    res.register_advancement()
                    self.advance()
                factor = CallNode(factor, arg_nodes)
            elif self.current_tok.type == TT_DOT:
                res.register_advancement()
                self.advance()

                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        self.current_tok.get_error_message()
                    ))

                prop_tok = self.current_tok
                
                res.register_advancement()
                self.advance()
                factor = DotNotationNode(factor, prop_tok)
            else:
                if self.current_tok.type != TT_LSQUARE:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        self.current_tok.get_error_message()
                    ))     

                res.register_advancement()
                self.advance()
                prop_node = res.register(self.expr())
                if res.error: return res

                if self.current_tok.type != TT_RSQUARE:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        self.current_tok.get_error_message()
                    ))     

                res.register_advancement()
                self.advance()

                factor = BracketNotationNode(factor, prop_node)
                    
        return res.success(factor)

    def term(self):
        return self.bin_op(self.call, (TT_MUL, TT_DIV))

    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def comp_expr(self):
        return self.bin_op(self.arith_expr, (TT_LT, TT_LTE, TT_GT, TT_GTE, (TT_KEYWORD, 'is')))
    
    def eq_expr(self):
        return self.bin_op(self.comp_expr, (TT_EE, TT_NE))
    
    def band_expr(self):
        return self.bin_op(self.eq_expr, (TT_BITAND, ))
    
    def bxor_expr(self):
        return self.bin_op(self.band_expr, (TT_BITXOR, ))
    
    def bor_expr(self):
        return self.bin_op(self.bxor_expr, (TT_BITOR, ))
    
    def and_expr(self):
        return self.bin_op(self.bor_expr, (TT_AND, ))
    
    def xor_expr(self):
        return self.bin_op(self.and_expr, (TT_XOR, ))
    
    def or_expr(self):
        return self.bin_op(self.xor_expr, (TT_OR, ))

    def assignment_expr(self):
        return self.bin_op(self.or_expr, (
            TT_EQ, 
            TT_PLUSEQ, 
            TT_MINUSEQ, 
            TT_MULEQ,
            TT_DIVEQ,
            TT_BITANDEQ,
            TT_BITOREQ,
            TT_BITXOREQ
        ))

    def expr(self):
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD, 'return'):
            pos_start = self.current_tok.pos_start.copy()

            res.register_advancement()
            self.advance()

            expr = res.register(self.expr())
            if res.error: return res

            return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_end.copy()))
            
        if self.current_tok.matches(TT_KEYWORD, 'var'):
            var_declare_expr = res.register(self.var_assign_expr())
            if res.error: return res
            return res.success(var_declare_expr)

        return self.assignment_expr()

    def curly_expr(self):
        res = ParseResult()
        
        if self.current_tok.type != TT_LCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                self.current_tok.get_error_message()
            ))

        res.register_advancement()
        self.advance()
        while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

        if self.current_tok.type == TT_RCURLY:
            tok = self.current_tok
            res.register_advancement()
            self.advance()
            statements = NilNode(tok)
        else:
            statements = res.register(self.statements())

            if res.error: return res
            if self.current_tok.type != TT_RCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    self.current_tok.get_error_message()
                ))

            res.register_advancement()
            self.advance()
        
        return res.success(statements)

    def var_assign_expr(self):
        res = ParseResult()
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                self.current_tok.get_error_message()
            ))
        
        var_name = self.current_tok
        
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_EQ:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                self.current_tok.get_error_message()
            ))

        res.register_advancement()
        self.advance()

        expr = res.register(self.expr())
        if res.error: return res

        return res.success(VarAssignNode(var_name, expr))

    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()
        
        if self.current_tok.type == TT_EOF:
            statements.append(NilNode(self.current_tok))
        else:
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

    def bin_op(self, func_a, ops, func_b=None):
        if func_b == None:
            func_b = func_a
        
        res = ParseResult()
        left = res.register(func_a())
        if res.error: return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)
    

            
#######################################
# RUNTIME RESULT
#######################################

class RTResult:
    def __init__(self):
        self.reset()

    def reset(self):
        self.value = None
        self.error = None
        self.func_return_value = None

    def register(self, res):
        self.error = res.error
        self.func_return_value = res.func_return_value
        return res.value

    def success(self, value):
        # self.reset()
        self.value = value
        return self

    def success_return(self, value):
        # self.reset()
        self.func_return_value = value
        return self
    
    def success_continue(self):
        self.reset()
        self.loop_should_continue = True
        return self

    def success_break(self):
        self.reset()
        self.loop_should_break = True
        return self

    def failure(self, error):
        self.reset()
        self.error = error
        return self

    def should_return(self):
        # Note: this will allow you to continue and break outside the current function
        return (
            self.error or
            self.func_return_value or
            self.loop_should_continue or
            self.loop_should_break
        )
        

#######################################
# VALUES
#######################################
class Object:
    def __init__(self, prototype=None):
        if not prototype: prototype = self

        self.keys = []
        self.values = []
        self.prototype = prototype
        self.uuid = uuid.uuid4()

        self.set_pos()
        self.set_context()
        self.set_name()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        if not (hasattr(self, 'context') and self.context):
            self.context = context
        return self
    
    def set_name(self, name='<anonymous>'):
        self.name = name
        return self
        
    def get(self, key, depth_decr=DEFAULT_MAX_DEPTH, ignore_prototype=False):
        if depth_decr < 0: return

        key = str(key)
        if key in self.keys:
                return self.values[self.keys.index(key)]
        else:
            if self.prototype and (not ignore_prototype):
                return self.prototype.get(key, depth_decr-1, ignore_prototype)

    def set(self, key, value):
        key = str(key)
        if key in self.keys:
            self.values[self.keys.index(key)] = value
        else:
            self.keys.append(key)
            self.values.append(value)
            
    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        return None, self.illegal_operation(other)

    def multed_by(self, other):
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        return None, self.illegal_operation(other)

    def negated(self):
        return None, self.illegal_operation()

    def get_comparison_eq(self, other):
        return Bool(self.uuid == other.uuid), None
    
    def get_comparison_ne(self, other):
        return Bool(self.uuid != other.uuid), None
    
    def get_comparison_lt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lte(self, other):
        return None, self.illegal_operation(other)
    
    def get_comparison_gte(self, other):
        return None, self.illegal_operation(other)
    
    def is_(self, other):
        temp = self.prototype
        i = 0
        while temp and i < DEFAULT_MAX_DEPTH:
            if temp.uuid == other.uuid: return Bool(True), None
            temp = temp.prototype
            i += 1

        return Bool(False), None
    
    def anded_by(self, other):
        return None, self.illegal_operation(other)

    def ored_by(self, other):
        return None, self.illegal_operation(other)
    
    def xored_by(self, other):
        return None, self.illegal_operation(other)

    def notted(self):
        return None, self.illegal_operation()
    
    def bitanded_by(self, other):
        return None, self.illegal_operation(other)
    
    def bitored_by(self, other):
        return None, self.illegal_operation(other)
    
    def bitxored_by(self, other):
        return None, self.illegal_operation(other)
    
    def bitnotted(self):
        return None, self.illegal_operation()

    def execute(self, args, pos_start, pos_end):
        return RTResult().failure(self.illegal_operation())

    def is_true(self):
        return True

    def illegal_operation(self, other=None):
        if not other: other = self
        return RTError(
            self.pos_start, other.pos_end,
            'illegal operation',
            self.context
        )

    def __repr__(self):
        return f'{self.prototype.name}@{format(hash(self.uuid), "x")}'


class Nil(Object):
    def __init__(self):
        super().__init__(nil_object)
    
    def is_true(self):
        return False
        
    def __repr__(self):
        return 'nil'
        
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
                    'integer division by zero',
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

    def get_comparison_eq(self, other):
        if isinstance(other, (Int, Float)):
            return Bool(self.value == other.value).set_context(self.context), None
        else:
            return Bool(False), None

    def get_comparison_ne(self, other):
        if isinstance(other, (Int, Float)):
            return Bool(self.value != other.value).set_context(self.context), None
        else:
            return Bool(True), None
    
    def get_comparison_lt(self, other):
        if isinstance(other, (Int, Float)):
            return Bool(self.value < other.value).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)
            
    def get_comparison_gt(self, other):
        if isinstance(other, (Int, Float)):
            return Bool(self.value > other.value).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)
            
    def get_comparison_lte(self, other):
        if isinstance(other, (Int, Float)):
            return Bool(self.value <= other.value).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)
            
    def get_comparison_gte(self, other):
        if isinstance(other, (Int, Float)):
            return Bool(self.value >= other.value).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)

    def bitanded_by(self, other):
        if isinstance(other, Int):
            result = self.value & other.value
            return Int(result).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)

    def bitored_by(self, other):
        if isinstance(other, Int):
            result = self.value | other.value
            return Int(result).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)

    def bitxored_by(self, other):
        if isinstance(other, Int):
            result = self.value ^ other.value
            return Int(result).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)

    def bitnotted(self):
        return Int(~self.value).set_context(self.context), None

    def is_true(self):
        return self.value != np.int64(0)
        
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

    def get_comparison_eq(self, other):
        if isinstance(other, (Int, Float)):
            return Bool(self.value == other.value).set_context(self.context), None
        else:
            return Bool(False), None

    def get_comparison_ne(self, other):
        if isinstance(other, (Int, Float)):
            return Bool(self.value != other.value).set_context(self.context), None
        else:
            return Bool(True), None
    
    def get_comparison_lt(self, other):
        if isinstance(other, (Int, Float)):
            return Bool(self.value < other.value).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)
            
    def get_comparison_gt(self, other):
        if isinstance(other, (Int, Float)):
            return Bool(self.value > other.value).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)
            
    def get_comparison_lte(self, other):
        if isinstance(other, (Int, Float)):
            return Bool(self.value <= other.value).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)
            
    def get_comparison_gte(self, other):
        if isinstance(other, (Int, Float)):
            return Bool(self.value >= other.value).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)

    def is_true(self):
        return self.value != 0.0
        
    def __repr__(self):
        return f'{self.value}'
        
class Bool(Object):
    def __init__(self, value):
        super().__init__(bool_object)
        self.value = not not value

    def get_comparison_eq(self, other):
        if isinstance(other, Bool):
            return Bool(self.value == other.value).set_context(self.context), None
        else:
            return Bool(False).set_context(self.context), None

    def get_comparison_ne(self, other):
        if isinstance(other, Bool):
            return Bool(self.value != other.value).set_context(self.context), None
        else:
            return Bool(True).set_context(self.context), None

    def anded_by(self, other):
        if isinstance(other, Bool):
            return Bool(self.value and other.value).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)

    def ored_by(self, other):
        if isinstance(other, Bool):
            return Bool(self.value or other.value).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)

    def xored_by(self, other):
        if isinstance(other, Bool):
            return Bool(self.value != other.value).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)

    def notted(self):
        return Bool(not self.value).set_context(self.context), None

    def is_true(self):
        return self.value

    def __repr__(self):
        return 'true' if self.value else 'false'

class String(Object):
    def __init__(self, value):
        super().__init__(string_object)
        self.value = value
    
    def added_to(self, other):
        if isinstance(other, String):
            result = self.value + other.value
            return String(result).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)

    def get_comparison_eq(self, other):
        if isinstance(other, String):
            return Bool(self.value == other.value).set_context(self.context), None
        else:
            return Bool(False).set_context(self.context), None

    def get_comparison_ne(self, other):
        if isinstance(other, String):
            return Bool(self.value != other.value).set_context(self.context), None
        else:
            return Bool(True).set_context(self.context), None

    def is_true(self):
        return len(self.value) > 0
    
    def __repr__(self):
        return self.value

class List(Object):
    def __init__(self, elements):
        super().__init__(list_object)
        self.elements = elements

    def added_to(self, other):
        if isinstance(other, List):
            result = self.elements + other.elements
            return List(result).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)

    def __repr__(self):
        return str(self.elements)

class Tuple(Object):
    def __init__(self, elements):
        super().__init__(tuple_object)
        self.elements = elements

    def added_to(self, other):
        if isinstance(other, Tuple):
            result = self.elements + other.elements
            return Tuple(result).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)

    def __repr__(self):
        return repr(self.elements)

class BaseFunction(Object):
    def __init__(self, name):
        super().__init__(function_object)
        self.set_name(name or '<anonymous>')

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(Object(new_context.parent.symbol_table.object))
        return new_context
    
    def normalize_args(self, pos_start, pos_end, arg_names, args):
        # print(self.name, args)
        while len(args) < len(arg_names):
            args.append(Nil().set_pos(pos_start, pos_end))

        return args
    
    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(len(arg_names)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.object.set(arg_name, arg_value)
    
    def normalize_and_populate_args(self, pos_start, pos_end, arg_names, args, exec_ctx):
        args = self.normalize_args(pos_start, pos_end, arg_names, args)
        self.populate_args(arg_names, args, exec_ctx)
     
    def __repr__(self):
        return f'<function {self.name}>'

class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names):
        super().__init__(name)
        self.name = name
        self.body_node = body_node
        self.arg_names = arg_names

    def execute(self, args, pos_start, pos_end):
        res = RTResult()
        interpreter = Interpreter()
        # print(self.context.display_name)
        new_context = self.generate_new_context()

        self.normalize_and_populate_args(
            pos_start, pos_end, 
            self.arg_names, args, new_context
        )

        value = res.register(interpreter.visit(self.body_node, new_context))
        if res.error: return res

        return res.success(value)
    
class BuiltInFunction(BaseFunction):
    def __init__(self, name, method, arg_names):
        super().__init__(name)
        self.method = method
        self.arg_names = arg_names

    def execute(self, args, pos_start, pos_end):
        res = RTResult()
        exec_ctx = self.generate_new_context()
                
        self.normalize_and_populate_args(
            pos_start, pos_end,
            self.arg_names, args, exec_ctx
        )

        return_value = res.register(self.method(self.pos_start, self.pos_end, exec_ctx))
        if res.error: return res

        return res.success(return_value)


#######################################
# OBJECTS
#######################################
object_object = Object().set_name('Object')
nil_object = Object(object_object).set_name('Nil')
int_object = Object(object_object).set_name('Int')
float_object = Object(object_object).set_name('Float')
bool_object = Object(object_object).set_name('Bool')
string_object = Object(object_object).set_name('String')
list_object = Object(object_object).set_name('List')
tuple_object = Object(object_object).set_name('Tuple')
function_object = Object(object_object).set_name('Function')
system_object = Object(object_object).set_name('System')
math_object = Object(object_object).set_name('Math')

#######################################
# CONTEXT
#######################################
class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None, should_display=False):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None
        self.should_display = should_display

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

    def visit_NilNode(self, node, context):
        return RTResult().success(
            Nil().set_context(context).set_pos(node.pos_start, node.pos_end)
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

    def visit_BoolNode(self, node, context):
        return RTResult().success(
            Bool(node.tok.value == 'true').set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_StringNode(self, node, context):
        return RTResult().success(
            String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_ListNode(self, node, context):
        res = RTResult()
        elements = []

        for element_node in node.element_nodes:
            elements.append(res.register(self.visit(element_node, context)))
            if res.error: return res

        return res.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_TupleNode(self, node, context):
        res = RTResult()
        elements = []

        for element_node in node.element_nodes:
            elements.append(res.register(self.visit(element_node, context)))
            if res.error: return res

        return res.success(
            Tuple(tuple(elements)).set_context(context).set_pos(node.pos_start, node.pos_end)
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
     
    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        old_value = context.symbol_table.object.get(var_name, ignore_prototype=True)

        if old_value:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f'"{var_name}" is already defined',
                context
            ))
        
        value = res.register(self.visit(node.value_node, context))
        if res.error: return res

        context.symbol_table.object.set(var_name, value.set_name(var_name))
        return res.success(value)
          
    def visit_StatementsNode(self, node, context):
        res = RTResult() 
        lines = []
        for i in range(0, len(node.element_nodes)):
            line = res.register(self.visit(node.element_nodes[i], context))
            if res.error: return res
            lines.append(line)
        
        return res.success(lines[-1])

    def in_place_op(self, node, context, op):
            res = RTResult()

            left = res.register(self.visit(node.left_node, context))
            if res.error: return res

            right = res.register(self.visit(node.right_node, context))
            if res.error: return res

            if isinstance(node.left_node, VarAccessNode):
                var_name = node.left_node.var_name_tok.value

                old_value = res.register(self.visit(node.left_node, context))
                if res.error: return res
                
                value, error = op(old_value, right)
                if error: return res.failure(error)

                old_value.context.symbol_table.object.set(var_name, value)
                return res.success(value)
            elif isinstance(node.left_node, DotNotationNode):
                obj = res.register(self.visit(node.left_node.obj_node, context))
                if res.error: return res

                prop = node.left_node.prop_tok.value

                old_value = res.register(self.visit(node.left_node, context))
                if res.error: return res

                value, error = op(old_value, right)
                if error: return res.failure(error)

                obj.set(prop, value)            
                return res.success(value)
            elif isinstance(node.left_node, BracketNotationNode):
                obj = res.register(self.visit(node.left_node.obj_node, context))
                if res.error: return res

                prop = res.register(self.visit(node.left_node.prop_node, context))
                if res.error: return res

                old_value = res.register(self.visit(node.left_node, context))
                if res.error: return res

                value, error = op(old_value, right)
                if error: return res.failure(error)

                obj.set(prop, value)            
                return res.success(value)
            else:
                return res.failure(RTError(
                    node.left_node.pos_start, node.left_node.pos_end,
                    'invalid left-hand side in assignment',
                    context
                ))
    
    def visit_BinOpNode(self, node, context):
        # print('found bin op node!')
        res = RTResult()

        left = res.register(self.visit(node.left_node, context))
        if res.error: return res
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
            if isinstance(node.left_node, VarAccessNode):
                var_name = node.left_node.var_name_tok.value

                old_value = res.register(self.visit(node.left_node, context))
                if res.error: return res
                
                value = right

                old_value.context.symbol_table.object.set(var_name, value)
                return res.success(value)
            elif isinstance(node.left_node, DotNotationNode):
                obj = res.register(self.visit(node.left_node.obj_node, context))
                if res.error: return res

                prop = node.left_node.prop_tok.value
                value = right

                obj.set(prop, value)
                return res.success(value)
            elif isinstance(node.left_node, BracketNotationNode):
                obj = res.register(self.visit(node.left_node.obj_node, context))
                if res.error: return res

                prop = res.register(self.visit(node.left_node.prop_node, context))
                if res.error: return res
                
                value = right

                obj.set(prop, value)
                return res.success(value)
            else:
                return res.failure(RTError(
                    node.left_node.pos_start, node.left_node.pos_end,
                    'invalid left-hand side in assignment',
                    context
                ))

        elif node.op_tok.type == TT_EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == TT_NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_tok.type == TT_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == TT_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.type == TT_LTE:
            result, error = left.get_comparison_lte(right)
        elif node.op_tok.type == TT_GTE:
            result, error = left.get_comparison_gte(right)
        elif node.op_tok.matches(TT_KEYWORD, 'is'):
            result, error = left.is_(right)
        elif node.op_tok.type == TT_AND:
            result, error = left.anded_by(right)
        elif node.op_tok.type == TT_OR:
            result, error = left.ored_by(right)
        elif node.op_tok.type == TT_XOR:
            result, error = left.xored_by(right)
        elif node.op_tok.type == TT_BITAND:
            result, error = left.bitanded_by(right)
        elif node.op_tok.type == TT_BITOR:
            result, error = left.bitored_by(right)
        elif node.op_tok.type == TT_BITXOR:
            result, error = left.bitxored_by(right)
        elif node.op_tok.type == TT_PLUSEQ:
            result = res.register(self.in_place_op(node, context, lambda x, y: x.added_to(y)))
            if res.error: return res
            return res.success(result)
        elif node.op_tok.type == TT_MINUSEQ:
            result = res.register(self.in_place_op(node, context, lambda x, y: x.subbed_by(y)))
            if res.error: return res
            return res.success(result)
        elif node.op_tok.type == TT_MULEQ:
            result = res.register(self.in_place_op(node, context, lambda x, y: x.multed_by(y)))
            if res.error: return res
            return res.success(result)
        elif node.op_tok.type == TT_DIVEQ:
            result = res.register(self.in_place_op(node, context, lambda x, y: x.dived_by(y)))
            if res.error: return res
            return res.success(result)
        elif node.op_tok.type == TT_BITANDEQ:
            result = res.register(self.in_place_op(node, context, lambda x, y: x.bitanded_by(y)))
            if res.error: return res
            return res.success(result)
        elif node.op_tok.type == TT_BITOREQ:
            result = res.register(self.in_place_op(node, context, lambda x, y: x.bitored_by(y)))
            if res.error: return res
            return res.success(result)
        elif node.op_tok.type == TT_BITXOREQ:
            result = res.register(self.in_place_op(node, context, lambda x, y: x.bitxored_by(y)))
            if res.error: return res
            return res.success(result)

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
        elif node.op_tok.type == TT_NOT:
            number, error = number.notted()
        elif node.op_tok.type == TT_BITNOT:
            number, error = number.bitnotted()
        
        if error: return res.failure(error)
        return res.success(number.set_pos(node.pos_start, node.pos_end))


    def visit_IfNode(self, node, context): 
        new_context = Context('if statement', context, node.pos_start)
        new_context.symbol_table = SymbolTable(Object(new_context.parent.symbol_table.object))

        res = RTResult()
        condition = res.register(self.visit(node.condition, new_context))
        if res.error: return res

        if condition.is_true():
            if_case = res.register(self.visit(node.if_case, new_context))
            if res.error: return res

            return res.success(if_case)
        else:
            return res.success(Nil().set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_IfElseNode(self, node, context): 
        if_context = Context('if statement', context, node.pos_start)
        if_context.symbol_table = SymbolTable(Object(if_context.parent.symbol_table.object))

        res = RTResult()
        condition = res.register(self.visit(node.condition, if_context))
        if res.error: return res

        if condition.is_true():
            if_case = res.register(self.visit(node.if_case, if_context))
            if res.error: return res

            return res.success(if_case)
        else:
            else_context = Context('if statement', context, node.pos_start)
            else_context.symbol_table = SymbolTable(Object(else_context.parent.symbol_table.object))

            else_case = res.register(self.visit(node.else_case, else_context))
            if res.error: return res

            return res.success(else_case)

    def visit_ForNode(self, node, context): 
        res = RTResult()
        new_context = Context('for loop', context, node.pos_start)
        new_context.symbol_table = SymbolTable(Object(new_context.parent.symbol_table.object))

        statement1 = res.register(self.visit(node.statement1_node, new_context))
        if res.error: return res

        while True:
            statement2 = res.register(self.visit(node.statement2_node, new_context))
            if res.error: return res

            statement3 = res.register(self.visit(node.statement3_node, new_context))
            if res.error: return res
            

            if not statement2.is_true(): break

            body = res.register(self.visit(node.body_node, new_context))
            if res.error: return res
        
        return res.success(
            Nil().set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_WhileNode(self, node, context):
        res = RTResult()
        new_context = Context('while loop', context, node.pos_start)
        new_context.symbol_table = SymbolTable(Object(new_context.parent.symbol_table.object))

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.error: return res

            if not condition.is_true(): break

            res.register(self.visit(node.body_node, new_context))
            if res.error: return res

        return res.success(
            Nil().set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_FuncDefNode(self, node, context):
        res = RTResult()

        func_name = node.var_name_tok.value if node.var_name_tok else '<anonymous>'
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        func_value = Function(func_name, body_node, arg_names).set_context(context).set_pos(node.pos_start, node.pos_end)
            

        if node.var_name_tok:
            old_value = context.symbol_table.object.get(func_name, ignore_prototype=True)

            if old_value:
                return res.failure(RTError(
                    node.pos_start, node.pos_end,
                    f'"{func_name}" is already defined',
                    context
                ))
        
            context.symbol_table.object.set(func_name, func_value)

        return res.success(func_value)

    def visit_CallNode(self, node, context):
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.error: return res
        value_to_call = value_to_call.set_pos(node.pos_start, node.pos_end)

        if isinstance(value_to_call, BaseFunction) and value_to_call.arg_names and value_to_call.arg_names[0] == 'this' and isinstance(node.node_to_call, (DotNotationNode, BracketNotationNode)):
            obj = res.register(self.visit(node.node_to_call.obj_node, context))
            if res.error: return res
            args.append(obj)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.error: return res


        return_value = res.register(value_to_call.execute(args, node.pos_start, node.pos_end))
        if res.error: return res
        if not res.func_return_value:
            return res.success(Nil().set_context(context).set_pos(node.pos_start, node.pos_end))
        
        return res.success(res.func_return_value.set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_DotNotationNode(self, node, context):
        res = RTResult()
        obj = res.register(self.visit(node.obj_node, context))
        if res.error: return res

        prop = node.prop_tok.value

        result = obj.get(prop)
        if result == None:
            return res.success(
                Nil().set_context(context).set_pos(node.pos_start, node.pos_end)
            )
        else:
            return res.success(result.set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_BracketNotationNode(self, node, context):
        res = RTResult()
        obj = res.register(self.visit(node.obj_node, context))
        if res.error: return res
        
        prop = res.register(self.visit(node.prop_node, context))
        if res.error: return res
        
        result = obj.get(prop)
        if result == None:
            return res.success(
                Nil().set_context(context).set_pos(node.pos_start, node.pos_end)
            )
        else:
            return res.success(result.set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_ReturnNode(self, node, context):
        res = RTResult()
        expr = res.register(self.visit(node.node_to_return, context))
        if res.error: return res

        return res.success_return(expr).success(
            Nil().set_context(context).set_pos(node.pos_start, node.pos_end)
        )    

#######################################
# BUILT-IN FUNCTIONS
#######################################
def execute_object_new(pos_start, pos_end, exec_ctx):
    return RTResult().success_return(Object(object_object))

def execute_object_getPrototype(pos_start, pos_end, exec_ctx):
    this = exec_ctx.symbol_table.object.get('this')
    # print('getPrototype')

    return RTResult().success_return(this.prototype)

def execute_object_setPrototype(pos_start, pos_end, exec_ctx):
    this = exec_ctx.symbol_table.object.get('this')
    prototype = exec_ctx.symbol_table.object.get('prototype')

    this.prototype = prototype

    return RTResult().success_return(this)

def execute_object_toString(pos_start, pos_end, exec_ctx):
    this = exec_ctx.symbol_table.object.get('this')
    return RTResult().success_return(String(str(this)))

def execute_object_hashCode(pos_start, pos_end, exec_ctx):
    this = exec_ctx.symbol_table.object.get('this')
    return RTResult().success_return(Int(hash(this.uuid)))

def execute_object_getKeys(pos_start, pos_end, exec_ctx):
    this = exec_ctx.symbol_table.object.get('this')
    return RTResult().success_return(List([String(str(key)) for key in this.keys][:]))

def execute_object_getValues(pos_start, pos_end, exec_ctx):
    this = exec_ctx.symbol_table.object.get('this')
    return RTResult().success_return(List(this.values[:]))


def execute_nil_new(pos_start, pos_end, exec_ctx):
    return RTResult().success_return(Nil())


def execute_int_new(pos_start, pos_end, exec_ctx):
    return RTResult().success_return(Int(0))

def execute_int_intValue(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    if not isinstance(this, Int):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int',
            exec_ctx
        ))

    return res.success_return(this)

def execute_int_floatValue(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    if not isinstance(this, Int):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int',
            exec_ctx
        ))

    return res.success_return(Float(float(this.value)))

def execute_int_parseInt(pos_start, pos_end, exec_ctx):
    res = RTResult()
    str = exec_ctx.symbol_table.object.get('str')
    if not isinstance(str, String):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a String',
            exec_ctx
        ))

    try:
        return res.success_return(Int(np.int64(np.clip(int(str.value), I64_MIN_VALUE, I64_MAX_VALUE))))
    except ValueError:
        return res.success_return(Nil())


def execute_float_new(pos_start, pos_end, exec_ctx):
    return RTResult().success_return(Float(0.0))

def execute_float_intValue(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    if not isinstance(this, Float):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be float',
            exec_ctx
        ))

    return res.success_return(Int(np.int64(np.clip(int(this.value), I64_MIN_VALUE, I64_MAX_VALUE))))

def execute_float_floatValue(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    if not isinstance(this, Float):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be float',
            exec_ctx
        ))

    return res.success_return(this)

def execute_float_parseFloat(pos_start, pos_end, exec_ctx):
    res = RTResult()
    str = exec_ctx.symbol_table.object.get('str')
    if not isinstance(str, String):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a String',
            exec_ctx
        ))

    try:
        return res.success_return(Float(float(str.value)))
    except ValueError:
        return res.success_return(Nil())



def execute_bool_new(pos_start, pos_end, exec_ctx):
    return RTResult().success_return(Bool(False))

def execute_bool_intValue(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    if not isinstance(this, Bool):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a Bool',
            exec_ctx
        ))

    return res.success_return(Int(np.int64(1 if this.value else 0)))

def execute_bool_floatValue(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    if not isinstance(this, Bool):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a Bool',
            exec_ctx
        ))

    return res.success_return(Float(1.0 if this.value else 0.0))


def execute_string_new(pos_start, pos_end, exec_ctx):
    return RTResult().success_return(String(''))

def execute_string_length(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    if not isinstance(this, String):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a String',
            exec_ctx
        ))

    return RTResult().success_return(Int(np.int64(len(this.value))))

def execute_string_charAt(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    index = exec_ctx.symbol_table.object.get('index')
    if not isinstance(this, String):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a String',
            exec_ctx
        ))

    if not isinstance(index, Int):
        return res.failure(RTError(
            pos_start, pos_end,
            'second argument must be an Int',
            exec_ctx
        ))

    try:
        return res.success_return(String(this.value[index.value]))
    except IndexError:
        return res.success_return(Nil())

def execute_string_indexOf(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    str = exec_ctx.symbol_table.object.get('str')
    if not isinstance(this, String):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a String',
            exec_ctx
        ))

    if not isinstance(str, String):
        return res.failure(RTError(
            pos_start, pos_end,
            'second argument must be a String',
            exec_ctx
        ))

    try:
        return res.success_return(Int(this.value.index(str.value)))
    except ValueError:
        return res.success_return(Nil())

def execute_string_lastIndexOf(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    str = exec_ctx.symbol_table.object.get('str')
    if not isinstance(this, String):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a String',
            exec_ctx
        ))

    if not isinstance(str, String):
        return res.failure(RTError(
            pos_start, pos_end,
            'second argument must be a String',
            exec_ctx
        ))

    try:
        return res.success_return(Int(this.value.rindex(str.value)))
    except ValueError:
        return res.success_return(Nil())

def execute_string_substring(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    begin_index = exec_ctx.symbol_table.object.get('beginIndex')
    end_index = exec_ctx.symbol_table.object.get('endIndex')

    if not isinstance(this, String):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a String',
            exec_ctx
        ))

    if not isinstance(begin_index, Int):
        return res.failure(RTError(
            pos_start, pos_end,
            'second argument must be an Int',
            exec_ctx
        ))

    if isinstance(end_index, Nil):
            return res.success_return(String(this.value[begin_index.value:]))

    if not isinstance(end_index, Int):
        return res.failure(RTError(
            pos_start, pos_end,
            'third argument must be an Int or Nil',
            exec_ctx
        ))

    return res.success_return(String(this.value[begin_index.value:end_index.value]))

def execute_string_toLowerCase(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')

    if not isinstance(this, String):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a String',
            exec_ctx
        ))

    return res.success_return(String(this.value.lower()))

def execute_string_toUpperCase(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')

    if not isinstance(this, String):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a String',
            exec_ctx
        ))

    return res.success_return(String(this.value.upper()))


def execute_list_new(pos_start, pos_end, exec_ctx):
    return RTResult().success_return(List([]))

def execute_list_add(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    element = exec_ctx.symbol_table.object.get('element')
    if not isinstance(this, List):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a List',
            exec_ctx
        ))

    this.elements.append(element)

    return res.success_return(Nil())

def execute_list_clear(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    if not isinstance(this, List):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a List',
            exec_ctx
        ))

    this.elements.clear()

    return res.success_return(Nil())

def execute_list_get(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    index = exec_ctx.symbol_table.object.get('index')
    if not isinstance(this, List):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a List',
            exec_ctx
        ))

    if not isinstance(index, Int):
        return res.failure(RTError(
            pos_start, pos_end,
            'second argument must be an Int',
            exec_ctx
        ))    

    try:
        return res.success_return(this.elements[index.value])
    except IndexError:
        return res.success_return(Nil())

def execute_list_isEmpty(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    if not isinstance(this, List):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a List',
            exec_ctx
        ))

    return res.success_return(Bool(len(this.elements) == 0))

def execute_list_length(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    if not isinstance(this, List):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a List',
            exec_ctx
        ))

    return res.success_return(Int(len(this.elements)))

def execute_list_remove(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    index = exec_ctx.symbol_table.object.get('index')

    if not isinstance(this, List):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a List',
            exec_ctx
        ))

    if not isinstance(index, Int):
        return res.failure(RTError(
            pos_start, pos_end,
            'second argument must be an Int',
            exec_ctx
        ))

    result = Nil()
    try:
        result = this.value[index.value]
    except IndexError: pass

    try:
        this.elements.pop(index.value)
    except IndexError: pass
    
    return res.success(result)

def execute_list_set(pos_start, pos_end, exec_ctx):
    # print('HELLO?')

    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    index = exec_ctx.symbol_table.object.get('index')
    element = exec_ctx.symbol_table.object.get('element')

    if not isinstance(this, List):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a List',
            exec_ctx
        ))

    if not isinstance(index, Int):
        return res.failure(RTError(
            pos_start, pos_end,
            'second argument must be an Int',
            exec_ctx
        ))


    try:
        this.elements[index.value] = element
    except IndexError: 
        for i in range((index.value + 1) - (len(this.elements))):
            this.elements.append(Nil())
        
        # print(f'*** {len(this.elements)}')
        # print(index.value)
        this.elements[index.value] = element
    
    return res.success(element)


def execute_tuple_new(pos_start, pos_end, exec_ctx):
    return RTResult().success_return(Tuple(()))

def execute_tuple_get(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    index = exec_ctx.symbol_table.object.get('index')
    if not isinstance(this, Tuple):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a Tuple',
            exec_ctx
        ))

    if not isinstance(index, Int):
        return res.failure(RTError(
            pos_start, pos_end,
            'second argument must be an Int',
            exec_ctx
        ))    

    try:
        return res.success_return(this.elements[index.value])
    except IndexError:
        return res.success_return(Nil())

def execute_tuple_isEmpty(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    if not isinstance(this, Tuple):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a Tuple',
            exec_ctx
        ))

    return res.success_return(Bool(len(this.elements) == 0))

def execute_tuple_length(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    if not isinstance(this, Tuple):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a Tuple',
            exec_ctx
        ))

    return res.success_return(Int(len(this.elements)))

def execute_function_new(pos_start, pos_end, exec_ctx):
    def execute(pos_start, pos_end, exec_ctx):
        return RTResult().success(Nil())

    result = BuiltInFunction('<anonymous>', execute, [])

    return RTResult().success_return(result)

def execute_function_length(pos_start, pos_end, exec_ctx):
    res = RTResult()
    this = exec_ctx.symbol_table.object.get('this')
    if not isinstance(this, BaseFunction):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be a Function',
            exec_ctx
        ))

    return res.success_return(Int(len(this.arg_names)))


def execute_system_print(pos_start, pos_end, exec_ctx):
    print(str(exec_ctx.symbol_table.object.get('data')))
    return RTResult().success_return(Nil())

def execute_system_write(pos_start, pos_end, exec_ctx):
    print(str(exec_ctx.symbol_table.object.get('data')), end='')
    return RTResult().success_return(Nil())

def execute_system_prompt(pos_start, pos_end, exec_ctx):
    result = input()
    return RTResult().success_return(String(result))


def execute_math_sin(pos_start, pos_end, exec_ctx):
    res = RTResult()
    a = exec_ctx.symbol_table.object.get('a')
    if not isinstance(a, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int or Float',
            exec_ctx
        ))

    return res.success_return(to_skink_number(np.sin(a.value)))

def execute_math_cos(pos_start, pos_end, exec_ctx):
    res = RTResult()
    a = exec_ctx.symbol_table.object.get('a')
    if not isinstance(a, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int or Float',
            exec_ctx
        ))

    return res.success_return(to_skink_number(np.cos(a.value)))

def execute_math_tan(pos_start, pos_end, exec_ctx):
    res = RTResult()
    a = exec_ctx.symbol_table.object.get('a')
    if not isinstance(a, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int or Float',
            exec_ctx
        ))

    return res.success_return(to_skink_number(np.tan(a.value)))

def execute_math_asin(pos_start, pos_end, exec_ctx):
    res = RTResult()
    a = exec_ctx.symbol_table.object.get('a')
    if not isinstance(a, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int or Float',
            exec_ctx
        ))

    return res.success_return(to_skink_number(np.arcsin(a.value)))

def execute_math_acos(pos_start, pos_end, exec_ctx):
    res = RTResult()
    a = exec_ctx.symbol_table.object.get('a')
    if not isinstance(a, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int or Float',
            exec_ctx
        ))

    return res.success_return(to_skink_number(np.arccos(a.value)))

def execute_math_atan(pos_start, pos_end, exec_ctx):
    res = RTResult()
    a = exec_ctx.symbol_table.object.get('a')
    if not isinstance(a, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int or Float',
            exec_ctx
        ))

    return res.success_return(to_skink_number(np.arctan(a.value)))

def execute_math_atan2(pos_start, pos_end, exec_ctx):
    res = RTResult()
    a = exec_ctx.symbol_table.object.get('a')
    b = exec_ctx.symbol_table.object.get('b')

    if not isinstance(a, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int or Float',
            exec_ctx
        ))

    if not isinstance(b, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int or Float',
            exec_ctx
        ))

    return res.success_return(to_skink_number(np.arctan2(a.value, b.value)))

def execute_math_exp(pos_start, pos_end, exec_ctx):
    res = RTResult()
    a = exec_ctx.symbol_table.object.get('a')

    if not isinstance(a, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int or Float',
            exec_ctx
        ))

    return res.success_return(to_skink_number(np.exp(a.value)))

def execute_math_log(pos_start, pos_end, exec_ctx):
    res = RTResult()
    a = exec_ctx.symbol_table.object.get('a')

    if not isinstance(a, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int or Float',
            exec_ctx
        ))

    return res.success_return(to_skink_number(np.log(a.value)))

def execute_math_sqrt(pos_start, pos_end, exec_ctx):
    res = RTResult()
    a = exec_ctx.symbol_table.object.get('a')

    if not isinstance(a, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int or Float',
            exec_ctx
        ))

    return res.success_return(to_skink_number(np.sqrt(a.value)))

def execute_math_pow(pos_start, pos_end, exec_ctx):
    res = RTResult()
    a = exec_ctx.symbol_table.object.get('a')
    b = exec_ctx.symbol_table.object.get('b')

    if not isinstance(a, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int or Float',
            exec_ctx
        ))
    
    if not isinstance(b, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'second argument must be an Int or Float',
            exec_ctx
        ))

    return res.success_return(to_skink_number(np.power(a.value, b.value)))

def execute_math_ceil(pos_start, pos_end, exec_ctx):
    res = RTResult()
    a = exec_ctx.symbol_table.object.get('a')

    if not isinstance(a, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int or Float',
            exec_ctx
        ))
    
    return res.success_return(to_skink_number(np.ceil(a.value)))

def execute_math_floor(pos_start, pos_end, exec_ctx):
    res = RTResult()
    a = exec_ctx.symbol_table.object.get('a')

    if not isinstance(a, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int or Float',
            exec_ctx
        ))
    
    return res.success_return(to_skink_number(np.floor(a.value)))

def execute_math_round(pos_start, pos_end, exec_ctx):
    res = RTResult()
    a = exec_ctx.symbol_table.object.get('a')

    if not isinstance(a, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int or Float',
            exec_ctx
        ))
    
    return res.success_return(to_skink_number(np.floor(a.value + 0.5)))

def execute_math_random(pos_start, pos_end, exec_ctx):
    res = RTResult()
    return res.success_return(Float(np.random.rand()))

def execute_math_abs(pos_start, pos_end, exec_ctx):
    res = RTResult()
    a = exec_ctx.symbol_table.object.get('a')

    if not isinstance(a, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int or Float',
            exec_ctx
        ))
    
    return res.success_return(to_skink_number(np.abs(a.value)))

def execute_math_min(pos_start, pos_end, exec_ctx):
    res = RTResult()
    a = exec_ctx.symbol_table.object.get('a')
    b = exec_ctx.symbol_table.object.get('b')

    if not isinstance(a, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int or Float',
            exec_ctx
        ))
    
    if not isinstance(b, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'second argument must be an Int or Float',
            exec_ctx
        ))
    
    return res.success_return(to_skink_number(np.min(a.value, b.value)))

def execute_math_max(pos_start, pos_end, exec_ctx):
    res = RTResult()
    a = exec_ctx.symbol_table.object.get('a')
    b = exec_ctx.symbol_table.object.get('b')

    if not isinstance(a, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'first argument must be an Int or Float',
            exec_ctx
        ))
    
    if not isinstance(b, (Int, Float)):
        return res.failure(RTError(
            pos_start, pos_end,
            'second argument must be an Int or Float',
            exec_ctx
        ))
    
    return res.success_return(to_skink_number(np.max(a.value, b.value)))

object_new = BuiltInFunction('new', execute_object_new, [])
object_getPrototype = BuiltInFunction('getPrototype', execute_object_getPrototype, ['this'])
object_setPrototype = BuiltInFunction('setPrototype', execute_object_setPrototype, ['this', 'prototype'])
object_toString = BuiltInFunction('toString', execute_object_toString, ['this'])
object_hashCode = BuiltInFunction('hashCode', execute_object_hashCode, ['this'])
object_getKeys = BuiltInFunction('getKeys', execute_object_getKeys, ['this'])
object_getValues = BuiltInFunction('getValues', execute_object_getValues, ['this'])

nil_new = BuiltInFunction('new', execute_nil_new, [])

int_new = BuiltInFunction('new', execute_int_new, [])
int_intValue = BuiltInFunction('intValue', execute_int_intValue, ['this'])
int_floatValue = BuiltInFunction('floatValue', execute_int_floatValue, ['this'])
# int_toBase = BuiltInFunction('toBase', execute_int_toBase, ['this', 'radix'])
int_parseInt = BuiltInFunction('parseInt', execute_int_parseInt, ['str'])

float_new = BuiltInFunction('new', execute_float_new, [])
float_intValue = BuiltInFunction('intValue', execute_float_intValue, ['this'])
float_floatValue = BuiltInFunction('floatValue', execute_float_floatValue, ['this'])
float_parseFloat = BuiltInFunction('parseFloat', execute_float_parseFloat, ['str'])

bool_new = BuiltInFunction('new', execute_bool_new, [])
bool_intValue = BuiltInFunction('intValue', execute_bool_intValue, ['this'])
bool_floatValue = BuiltInFunction('floatalue', execute_bool_floatValue, ['this'])

string_new = BuiltInFunction('new', execute_string_new, [])
string_charAt = BuiltInFunction('charAt', execute_string_charAt, ['this', 'index'])
string_length = BuiltInFunction('length', execute_string_length, ['this'])
string_indexOf = BuiltInFunction('indexOf', execute_string_indexOf, ['this', 'str'])
string_lastIndexOf = BuiltInFunction('lastIndexOf', execute_string_lastIndexOf, ['this', 'str'])
string_substring = BuiltInFunction('substring', execute_string_substring, ['this', 'beginIndex', 'endIndex'])
string_toLowerCase = BuiltInFunction('toLowerCase', execute_string_toLowerCase, ['this'])
string_toUpperCase = BuiltInFunction('toUpperCase', execute_string_toUpperCase, ['this'])


list_new = BuiltInFunction('new', execute_list_new, [])
list_add = BuiltInFunction('add', execute_list_add, ['this', 'element'])
list_clear = BuiltInFunction('clear', execute_list_clear, ['this'])
list_get = BuiltInFunction('get', execute_list_get, ['this', 'index'])
list_isEmpty = BuiltInFunction('isEmpty', execute_list_isEmpty, ['this'])
list_length = BuiltInFunction('length', execute_list_length, ['this'])
list_remove = BuiltInFunction('remove', execute_list_remove, ['this', 'index'])
list_set = BuiltInFunction('set', execute_list_set, ['this', 'index', 'element'])
# list_transform = BuiltInFunction('transform', execute_list_transform, ['this', 'fn'])

tuple_new = BuiltInFunction('new', execute_tuple_new, [])
tuple_get = BuiltInFunction('get', execute_tuple_get, ['this', 'element'])
tuple_length = BuiltInFunction('length', execute_tuple_length, ['this'])
tuple_isEmpty = BuiltInFunction('isEmpty', execute_tuple_isEmpty, ['isEmpty'])

function_new = BuiltInFunction('new', execute_function_new, [])
function_length = BuiltInFunction('length', execute_function_length, ['this'])

system_print = BuiltInFunction('print', execute_system_print, ['data'])
system_write = BuiltInFunction('write', execute_system_write, ['data'])
system_prompt = BuiltInFunction('prompt', execute_system_prompt, [])

math_sin = BuiltInFunction('sin', execute_math_sin, ['a'])
math_cos = BuiltInFunction('cos', execute_math_cos, ['a'])
math_tan = BuiltInFunction('tan', execute_math_tan, ['a'])
math_asin = BuiltInFunction('asin', execute_math_asin, ['a'])
math_acos = BuiltInFunction('acos', execute_math_acos, ['a'])
math_atan = BuiltInFunction('atan', execute_math_atan, ['a'])
math_atan2 = BuiltInFunction('atan2', execute_math_atan2, ['a', 'b'])
math_exp = BuiltInFunction('exp', execute_math_exp, ['a'])
math_log = BuiltInFunction('log', execute_math_log, ['a'])
math_sqrt = BuiltInFunction('sqrt', execute_math_sqrt, ['a'])
math_pow = BuiltInFunction('pow', execute_math_pow, ['a', 'b'])
math_ceil = BuiltInFunction('ceil', execute_math_ceil, ['a'])
math_floor = BuiltInFunction('floor', execute_math_floor, ['a'])
math_round = BuiltInFunction('round', execute_math_round, ['a'])
math_random = BuiltInFunction('random', execute_math_random, [])
math_abs = BuiltInFunction('abs', execute_math_abs, ['a'])
math_min = BuiltInFunction('min', execute_math_min, ['a', 'b'])
math_max = BuiltInFunction('max', execute_math_max, ['a', 'b'])

#######################################
# RUN
#######################################
global_symbol_table = SymbolTable(Object(object_object))
global_symbol_table.object.set('global', global_symbol_table.object)

global_symbol_table.object.set('Object', object_object)
global_symbol_table.object.set('Nil', nil_object)
global_symbol_table.object.set('Int', int_object)
global_symbol_table.object.set('Float', float_object)
global_symbol_table.object.set('Bool', bool_object)
global_symbol_table.object.set('String', string_object)
global_symbol_table.object.set('List', list_object)
global_symbol_table.object.set('Tuple', tuple_object)
global_symbol_table.object.set('Function', function_object)
global_symbol_table.object.set('System', system_object)
global_symbol_table.object.set('Math', math_object)

object_object.set('new', object_new)
object_object.set('getPrototype', object_getPrototype)
object_object.set('setPrototype', object_setPrototype)
object_object.set('toString', object_toString)
object_object.set('hashCode', object_hashCode)
object_object.set('getKeys', object_getKeys)
object_object.set('getValues', object_getValues)

nil_object.set('new', nil_new)

int_object.set('MIN_VALUE', Int(I64_MIN_VALUE))
int_object.set('MAX_VALUE', Int(I64_MAX_VALUE))
int_object.set('new', int_new)
int_object.set('intValue', int_intValue)
int_object.set('floatValue', int_floatValue)
# int_object.set('toBase', int_toBase)
int_object.set('parseInt', int_parseInt)

float_object.set('MIN_VALUE', Float(FLOAT_MIN_VALUE))
float_object.set('MAX_VALUE', Float(FLOAT_MAX_VALUE))
float_object.set('new', float_new)
float_object.set('intValue', float_intValue)
float_object.set('floatValue', float_floatValue)
float_object.set('parseFloat', float_parseFloat)

bool_object.set('TRUE', Bool(True))
bool_object.set('FALSE', Bool(False))
bool_object.set('new', bool_new)
bool_object.set('intValue', bool_intValue)
bool_object.set('floatValue', bool_floatValue)

string_object.set('new', string_new)
string_object.set('charAt', string_charAt)
string_object.set('length', string_length)
string_object.set('indexOf', string_indexOf)
string_object.set('lastIndexOf', string_lastIndexOf)
string_object.set('substring', string_substring)
string_object.set('toLowerCase', string_toLowerCase)
string_object.set('toUpperCase', string_toUpperCase)

list_object.set('new', list_new)
list_object.set('add', list_add)
list_object.set('clear', list_clear)
list_object.set('get', list_get)
list_object.set('isEmpty', list_isEmpty)
list_object.set('length', list_length)
list_object.set('remove', list_remove)
list_object.set('set', list_set)

tuple_object.set('new', tuple_new)
tuple_object.set('get', tuple_get)
tuple_object.set('isEmpty', tuple_isEmpty)
tuple_object.set('length', tuple_length)

function_object.set('new', function_new)
function_object.set('length', function_length)

system_object.set('print', system_print)
system_object.set('write', system_write)
system_object.set('prompt', system_prompt)

math_object.set('E', Float(np.e))
math_object.set('PI', Float(np.pi))
math_object.set('sin', math_sin)
math_object.set('cos', math_cos)
math_object.set('tan', math_tan)
math_object.set('asin', math_asin)
math_object.set('acos', math_acos)
math_object.set('atan', math_atan)
math_object.set('atan2', math_atan2)
math_object.set('exp', math_exp)
math_object.set('log', math_log)
math_object.set('sqrt', math_sqrt)
math_object.set('pow', math_pow)
math_object.set('ceil', math_ceil)
math_object.set('floor', math_floor)
math_object.set('round', math_round)
math_object.set('random', math_random)
math_object.set('abs', math_abs)
math_object.set('min', math_min)
math_object.set('max', math_max)

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
    context = Context('<program>', should_display=True)
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)
    if result.error: return None, result.error

    return result.value, None

def run(fn):
    f = open(fn)
    display_fn = fn.split('/')[-1]

    return runstring(f.read(), display_fn)

