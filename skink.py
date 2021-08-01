# Skink source code
# Usage permitted under terms of MIT License

#######################################
# IMPORTS
#######################################
import numpy as np 
import uuid
import string
import sys
import time
import math

#######################################
# CONSTANTS
#######################################
DIGITS = '0123456789'
LETTERS = string.ascii_letters + '$_'
LETTERS_DIGITS = LETTERS + DIGITS
NEWLINES = '\n\r'
DEFAULT_MAX_DEPTH = 6

#######################################
# UTILITY FUNCTIONS
#######################################
def isPrototypeOf(a, b):
    while b:
        b = b.prototype
        if b and a.uuid == b.uuid: return True
    
    return False

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
        result  = f'{self.pos_start.fn}:{self.pos_start.ln + 1}:{self.pos_start.col + 1}: '
        result  += f'error: {self.details}'
        return result

class IllegalCharError(LangError):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class ExpectedCharError(LangError):
  def __init__(self, pos_start, pos_end, details):
    super().__init__(pos_start, pos_end, 'Expected Character', details)

class InvalidSyntaxError(LangError):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class RTError(LangError):
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
                result = f'\n\t{pos.fn}:{pos.ln + 1}:{pos.col + 1}: in {ctx.display_name}{result}'
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
TT_STRING   = 'STRING'
TT_IDENTIFIER = 'IDENTIFIER'
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
TT_DOT      = 'DOT'
TT_COMMA    = 'COMMA'
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
TT_PLUSEQ   = 'PLUSEQ'
TT_MINUSEQ  = 'MINUSEQ'
TT_MULEQ    = 'MULEQ'
TT_DIVEQ    = 'DIVEQ'
TT_BANDEQ   = 'BANDEQ'
TT_BOREQ    = 'BOREQ'
TT_BXOREQ   = 'BXOREQ'
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
    'func',
    'return'
]

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            if not pos_end:
                self.pos_end = pos_start.copy()
                self.pos_end.advance(None)
            else:
                self.pos_end = pos_end

    def get_error_message(self):
        # print(self.pos_start.idx)
        if self.type == TT_EOF: return 'unexpected end of input'
        # return 'token'
        
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
                token, error = self.make_string()
                if error: return [], error
                tokens.append(token)
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
            elif self.current_char == '.':
                tokens.append(Token(TT_DOT, pos_start=self.pos.copy()))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA, pos_start=self.pos.copy()))
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
                tokens.append(Token(TT_BNOT, pos_start=self.pos.copy()))
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
            clipped = np.clip(int(num_str), -(2 ** 63), 2 ** 63 - 1)
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
        tok_type = TT_BAND
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '&':
            self.advance()
            tok_type = TT_AND
        elif self.current_char == '=':
            self.advance()
            tok_type = TT_BANDEQ

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def make_or(self):
        tok_type = TT_BOR
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '|':
            self.advance()
            tok_type = TT_OR
        elif self.current_char == '=':
            self.advance()
            tok_type = TT_BOREQ

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def make_xor(self):
        tok_type = TT_BXOR
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '^':
            self.advance()
            tok_type = TT_XOR
        elif self.current_char == '=':
            self.advance()
            tok_type = TT_BXOREQ

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

#######################################
# NODES
#######################################
class EmptyNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

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

class ListNode:
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



class CallNode:
    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_start = self.node_to_call.pos_start

        if len(self.arg_nodes) > 0:
            self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end


class ReturnNode:
    def __init__(self, node):
        self.node = node

        self.pos_start = node.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.node})'

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

        if tok.type in (TT_PLUS, TT_MINUS, TT_NOT, TT_BNOT):
            res.register_advancement()
            self.advance()
            call = res.register(self.call())
            if res.error: return res
            return res.success(UnaryOpNode(tok, call))
        
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
                    self.current_tok.get_error_message()
                ))

        elif self.current_tok.matches(TT_KEYWORD, 'func'):
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
        return self.bin_op(self.arith_expr, (TT_LT, TT_LTE, TT_GT, TT_GTE))
    
    def eq_expr(self):
        return self.bin_op(self.comp_expr, (TT_EE, TT_NE))
    
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
        return self.bin_op(self.or_expr, (
            TT_EQ, 
            TT_PLUSEQ, 
            TT_MINUSEQ, 
            TT_MULEQ,
            TT_DIVEQ,
            TT_BANDEQ,
            TT_BOREQ,
            TT_BXOREQ
        ))

    def expr(self):
        res = ParseResult()

        while self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()
        
        if self.current_tok.matches(TT_KEYWORD, 'var'):
            var_declare_expr = res.register(self.var_declare_expr())
            if res.error: return res
            return res.success(var_declare_expr)
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
        elif self.current_tok.matches(TT_KEYWORD, 'return'):
            return_expr = res.register(self.return_expr())
            if res.error: return res
            return res.success(return_expr)
        return self.assignment_expr()

    def var_declare_expr(self):
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

        return res.success(VarDeclareNode(var_name, expr))
    

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
        if self.current_tok.type != TT_LCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                self.current_tok.get_error_message()
            ))

        res.register_advancement()
        self.advance()

        statements = res.register(self.statements())

        if res.error: return res
        if self.current_tok.type != TT_RCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                self.current_tok.get_error_message()
            ))

        res.register_advancement()
        self.advance()
        if self.current_tok.matches(TT_KEYWORD, 'else'): 
                res.register_advancement()
                self.advance()
                if self.current_tok.type != TT_LCURLY:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        self.current_tok.get_error_message()
                    ))

                res.register_advancement()
                self.advance()

                else_case = res.register(self.statements())

                if res.error: return res
                if self.current_tok.type != TT_RCURLY:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        self.current_tok.get_error_message()
                    ))

                res.register_advancement()
                self.advance()
                return res.success(IfElseNode(condition, statements, else_case))
        else: 
                return res.success(IfNode(condition, statements))            


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
        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()
            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f'Unexepcted {self.current_tok.display_text}'
                ))
        else:
            var_name_tok = None
            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f'Unexepcted {self.current_tok.display_text}'
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
                        self.current_tok.get_error_message()
                    ))

                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()
            
            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    self.current_tok.get_error_message()
                ))
        else:
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

        statements = res.register(self.statements())

        if res.error: return res
        if self.current_tok.type != TT_RCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                self.current_tok.get_error_message()
            ))

        res.register_advancement()
        self.advance()
        return res.success(FuncDefNode(
            var_name_tok,
            arg_name_toks,
            statements  
        ))

    def return_expr(self):
        res = ParseResult()
        res.register_advancement()
        self.advance()
        expr = res.register(self.expr())
        if res.error: return res

        return res.success(ReturnNode(expr))


    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != TT_LSQUARE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                self.current_tok.get_error_message()
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_RSQUARE:
            res.register_advancement()
            self.advance()
        else:
            element_nodes.append(res.register(self.expr()))
            if res.error:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    self.current_tok.get_error_message()
                ))

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
        self.reset()

    def reset(self):
        self.value = None
        self.error = None
        self.func_return_value = None

    def register(self, res):
        # print(res)
        self.error = res.error
        self.func_return_value = res.func_return_value
        # print(res.value)
        return res.value

    def success(self, value):
        # self.reset()
        self.value = value
        # print(self.value)
        return self

    def success_return(self, value):
        # self.reset()
        self.func_return_value = value
        # print(self.value)
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
    
    def anded_by(self, other):
        return None, self.illegal_operation(other)

    def ored_by(self, other):
        return None, self.illegal_operation(other)
    
    def xored_by(self, other):
        return None, self.illegal_operation(other)

    def notted(self):
        return None, self.illegal_operation()

    def banded_by(self, other):
        return None, self.illegal_operation(other)
    
    def bored_by(self, other):
        return None, self.illegal_operation(other)
    
    def bxored_by(self, other):
        return None, self.illegal_operation(other)
    
    def bnotted(self):
        return None, self.illegal_operation()

    def execute(self, args, context, pos_start, pos_end):
        return None, self.illegal_operation()

    def is_true(self):
        return True

    def illegal_operation(self, other=None):
        if not other: other = self
        return RTError(
            self.pos_start, other.pos_end,
            'illegal operation',
            self.context
        )
    
    def __repr__(self, depth_decr=DEFAULT_MAX_DEPTH):
        # print(depth_decr)
        keys = sorted(list(self.slots.keys()))
        values = [self.slots[key] for key in keys]

        if len(keys) == 0: return '{}'
        if depth_decr < 0:
            return '{...}'


        result = '{'
        for i in range(0, len(keys)-1):
            key = keys[i]
            value = values[i]

            use_depth_decr = type(value) in DEPTH_DECR_CLASSES

            value_str = value.__repr__(depth_decr - 1) if use_depth_decr else str(value)

            result += f'{key}: {value_str}, ' 
        
        key = keys[-1]
        value = values[-1]

        value_str = value.__repr__(depth_decr - 1) if type(value) == Object else str(value)

        result += f'{key}: {value_str}}}' 
        return result

class Nil(Object):
    def __init__(self):
        super().__init__(nil_object)
    
    def get_comparison_eq(self, other):
        return Bool(isinstance(other, Nil)), None

    def get_comparison_ne(self, other):
        return Bool(not isinstance(other, Nil)), None

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
            if str(other) == '0':
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'division by zero',
                    self.context
                )
            elif str(other) == '0.0':
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

    def banded_by(self, other):
        if isinstance(other, Int):
            result = self.value & other.value
            return Int(result).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)

    def bored_by(self, other):
        if isinstance(other, Int):
            result = self.value | other.value
            return Int(result).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)

    def bxored_by(self, other):
        if isinstance(other, Int):
            result = self.value ^ other.value
            return Int(result).set_context(self.context), None
        else:
            return None, Object.illegal_operation(self, other)

    def bnotted(self):
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
            if str(other) in ('0', '0.0'):
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
        self.value = value

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
            return String(self.value + other.value), None
        else:
            return None, self.illegal_operation(other)
    
    def get_comparison_eq(self, other):
        if isinstance(other, String):
            return Bool(self.value == other.value).set_context(self.context), None
        else:
            return Bool(False).set_context(self.context), None

    def get_comparison_ne(self, other):
        if isinstance(other, String):
            return Bool(self.value != other.value).set_context(self.context), None
        else:
            return Bool(False).set_context(self.context), None

    def is_true(self):
        return len(self.value) != 0

    def __repr__(self): 
        return self.value

class List(Object):
    def __init__(self, elements):
        super().__init__(list_object)
        for i in range(0, len(elements)):
            self.set(i, elements[i])

    def to_python_list(self):
        t1 = list(self.slots.keys())
        t2 = list(filter(lambda el: el.isnumeric(), t1))
        return [self.slots[el] for el in t2]

    def added_to(self, other):
        if isinstance(other, List): 
            return List(self.to_python_list() + other.to_python_list()), None
        else:
            return None, self.illegal_operation(other)
    
    def copy(self):
        return List(self.to_python_list()[:])

    # def is_true(self):
    #     return len(self.to_python_list()) != 0
       
    def __repr__(self, depth_decr=DEFAULT_MAX_DEPTH):
        if depth_decr < 0: return '[...]'
        t1 = ', '.join([el.__repr__(depth_decr-1) if type(el) in DEPTH_DECR_CLASSES else str(el) for el in self.to_python_list()])
        return f'[{t1}]'

class Function(Object):
    def __init__(self, name, func, is_member_function=False):
        super().__init__(function_object)
        self.name = name or '<anonymous>'
        self.func = func
        self.is_member_function = is_member_function
     
    def execute(self, args, context, pos_start, pos_end):
        return self.func(args, context, pos_start, pos_end)
  
    def __repr__(self):
        return f'<function {self.name}>'
        
#######################################
# OBJECTS
#######################################
object_object = Object()
nil_object = Object(object_object)
int_object = Object(object_object)
float_object = Object(object_object)
bool_object = Object(object_object)
string_object = Object(object_object)
list_object = Object(object_object)
function_object = Object(object_object)

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


    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.object.get(var_name)

        if not value:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f'{var_name} is not defined',
                context
            ))
        
        if not value.context: value.set_context(context)

        return res.success(value.set_pos(node.pos_start, node.pos_end))
     
    def visit_VarDeclareNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        old_value = context.symbol_table.object.slots.get(var_name, None)

        if old_value:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f'{var_name} is already defined',
                context
            ))
        
        value = res.register(self.visit(node.value_node, context))
        if res.error: return res

        context.symbol_table.object.set(var_name, value)
        return res.success(value)
          
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
            return res.success(result)

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
            return res.success(result)


    def visit_StatementsNode(self, node, context):
        res = RTResult() 
        lines = []
        for i in range(0, len(node.element_nodes)):
            line = res.register(self.visit(node.element_nodes[i], context))
            if res.error: return res
            # print(res.func_return_value)
            # print(res.value)
            if res.func_return_value: 
                return res.success(
                    Nil().set_context(context).set_pos(node.pos_start, node.pos_end)
                )
            
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

        # print(f'{left} {node.op_tok.type} {right}')
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
        elif node.op_tok.type == TT_AND:
            result, error = left.anded_by(right)
        elif node.op_tok.type == TT_OR:
            result, error = left.ored_by(right)
        elif node.op_tok.type == TT_XOR:
            result, error = left.xored_by(right)
        elif node.op_tok.type == TT_BAND:
            result, error = left.banded_by(right)
        elif node.op_tok.type == TT_BOR:
            result, error = left.bored_by(right)
        elif node.op_tok.type == TT_BXOR:
            result, error = left.bxored_by(right)
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
        elif node.op_tok.type == TT_BANDEQ:
            result = res.register(self.in_place_op(node, context, lambda x, y: x.banded_by(y)))
            if res.error: return res
            return res.success(result)
        elif node.op_tok.type == TT_BOREQ:
            result = res.register(self.in_place_op(node, context, lambda x, y: x.bored_by(y)))
            if res.error: return res
            return res.success(result)
        elif node.op_tok.type == TT_BXOREQ:
            result = res.register(self.in_place_op(node, context, lambda x, y: x.bxored_by(y)))
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
        elif node.op_tok.type == TT_BNOT:
            number, error = number.bnotted()
        
        if error: return res.failure(error)
        return res.success(number.set_pos(node.pos_start, node.pos_end))


    def visit_IfNode(self, node, context): 
        new_context = Context('if statement', context, node.pos_start)
        new_context.symbol_table = SymbolTable(Object(new_context.parent.symbol_table.object))

        res = RTResult()
        condition = res.register(self.visit(node.condition, context))
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
        condition = res.register(self.visit(node.condition, context))
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
            new_context_2 = Context('for loop', new_context, node.body_node.pos_start)
            new_context_2.symbol_table = SymbolTable(Object(new_context_2.parent.symbol_table.object))

            statement2 = res.register(self.visit(node.statement2_node, new_context))
            if res.error: return res

            statement3 = res.register(self.visit(node.statement3_node, new_context))
            if res.error: return res

            if not statement2.is_true(): break

            body = res.register(self.visit(node.body_node, new_context_2))
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

        def execute(args, context, pos_start, pos_end):
            for i in range(len(arg_names)):
                arg_name = arg_names[i]
                arg_value = args[i] if i < len(args) else Nil().set_pos(pos_start, pos_end)
                arg_value.set_context(context)
                context.symbol_table.object.set(arg_name, arg_value)

            context.symbol_table.object.set('argv', List(args))
            tmp = self.visit(body_node, context)
            func_return_value, error = tmp.func_return_value, tmp.error
            if error: return None, error

            return func_return_value or Nil().set_context(context).set_pos(pos_start, pos_end), None
        
        func_value = Function(func_name, execute).set_context(context).set_pos(node.pos_start, node.pos_end)
        
        if node.var_name_tok:
            old_value = context.symbol_table.object.slots.get(func_name, None)
            if old_value:
                return res.failure(RTError(
                    node.pos_start, node.pos_end,
                    f'{func_name} is already defined',
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

        new_context = Context(value_to_call.name if hasattr(value_to_call, 'name') else '<anonymous>', context, node.pos_start, True)
        new_context.symbol_table = SymbolTable(Object(new_context.parent.symbol_table.object))

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.error: return res

        if isinstance(value_to_call, Function) and value_to_call.is_member_function and isinstance(node.node_to_call, (DotNotationNode, BracketNotationNode)):
            obj = res.register(self.visit(node.node_to_call.obj_node, context))
            if res.error: return res

            return_value, error = value_to_call.execute(
                [obj] + args,
                context, node.pos_start, node.pos_end
            )

        else:
            return_value, error = value_to_call.execute(args, context, node.pos_start, node.pos_end)
        # print(return_value)
        if error: return res.failure(error)
        # print(f'{value_to_call.name} {args} {return_value}')

        return res.success(return_value.set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_ReturnNode(self, node, context):
        res = RTResult()
        expr = res.register(self.visit(node.node, context))
        if res.error: return res

        return res.success_return(expr).success(
            Nil().set_context(context).set_pos(node.pos_start, node.pos_end)
        )      

#######################################
# RUN
#######################################
DEPTH_DECR_CLASSES = (List, Object) 

global_symbol_table = SymbolTable(Object(object_object))
global_symbol_table.object.set('global', global_symbol_table.object)

def normalize_args(args, num_args, context, pos_start, pos_end):
    new_args = []
    for i in range(0, num_args):
        arg_value = args[i] if i < len(args) else Nil().set_context(context).set_pos(pos_start, pos_end)
        new_args.append(arg_value)
    
    return new_args

# def currentTimeMillis_func(args):
#     args = normalize_args(args, 0)
#     return Int(time.time_ns() // 1000000), None

def execute_numpy_ufunc(ufunc, args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)
    if not isinstance(args[0], (Int, Float)):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a number',
            context
        )

    result = ufunc(args[0].value)
    return Int(result) if isinstance(result, np.int64) else Float(result), None

def execute_abs(args, context, pos_start, pos_end):
    return execute_numpy_ufunc(
        np.abs,
        args, context, pos_start, pos_end
    )

def execute_acos(args, context, pos_start, pos_end):
    return execute_numpy_ufunc(
        np.acos,
        args, context, pos_start, pos_end
    )

def execute_acos(args, context, pos_start, pos_end):
    return execute_numpy_ufunc(
        np.acos,
        args, context, pos_start, pos_end
    )

def execute_asin(args, context, pos_start, pos_end):
    return execute_numpy_ufunc(
        np.asin,
        args, context, pos_start, pos_end
    )
    
def execute_atan(args, context, pos_start, pos_end):
    return execute_numpy_ufunc(
        np.atan,
        args, context, pos_start, pos_end
    )

def execute_atan2(args, context, pos_start, pos_end):
    args = normalize_args(args, 2, context, pos_start, pos_end)
    if not isinstance(args[0], (Int, Float)):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is a not a number',
            context
        )

    if not isinstance(args[1], (Int, Float)):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[1]} is a not a number',
            context
        )

    result = np.arctan2(args[0].value, args[1].value)
    return Int(result) if isinstance(result, np.int64) else Float(result), None

def execute_ceil(args, context, pos_start, pos_end):
    return execute_numpy_ufunc(
        np.ceil,
        args, context, pos_start, pos_end
    )

def execute_cos(args, context, pos_start, pos_end):
    return execute_numpy_ufunc(
        np.cos,
        args, context, pos_start, pos_end
    )

def execute_exp(args, context, pos_start, pos_end):
    return execute_numpy_ufunc(
        np.exp,
        args, context, pos_start, pos_end
    )

def execute_floor(args, context, pos_start, pos_end):
    return execute_numpy_ufunc(
        np.floor,
        args, context, pos_start, pos_end
    )

def execute_log(args, context, pos_start, pos_end):
    return execute_numpy_ufunc(
        np.log,
        args, context, pos_start, pos_end
    )

def execute_max(args, context, pos_start, pos_end):
    args = normalize_args(args, 2, context, pos_start, pos_end)
    if not isinstance(args[0], (Int, Float)):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is a not a number',
            context
        )

    if not isinstance(args[1], (Int, Float)):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[1]} is a not a number',
            context
        )

    result = np.max(np.array([args[0].value, args[1].value]))
    return Int(result) if isinstance(result, np.int64) else Float(result), None

def execute_min(args, context, pos_start, pos_end):
    args = normalize_args(args, 2, context, pos_start, pos_end)
    if not isinstance(args[0], (Int, Float)):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is a not a number',
            context
        )

    if not isinstance(args[1], (Int, Float)):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[1]} is a not a number',
            context
        )

    result = np.min(np.array([args[0].value, args[1].value]))
    return Int(result) if isinstance(result, np.int64) else Float(result), None


def execute_pow(args, context, pos_start, pos_end):
    args = normalize_args(args, 2, context, pos_start, pos_end)
    if not isinstance(args[0], (Int, Float)):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is a not a number',
            context
        )

    if not isinstance(args[1], (Int, Float)):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[1]} is a not a number',
            context
        )

    result = np.power(args[0].value, args[1].value)
    return Int(result) if isinstance(result, np.int64) else Float(result), None

def execute_print(args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)
    sys.stdout.write(repr(args[0]))
    return Nil(), None

def execute_println(args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)
    return Nil(), None

def execute_random(args, context, pos_start, pos_end):
    args = normalize_args(args, 0, context, pos_start, pos_end)
    result = np.random.rand()
    return Int(result) if isinstance(result, np.int64) else Float(result), None

def execute_round(args, context, pos_start, pos_end):
    return execute_numpy_ufunc(
        lambda x: np.floor(x + 0.5),
        args, context, pos_start, pos_end
    )

def execute_sin(args, context, pos_start, pos_end):
    return execute_numpy_ufunc(
        np.sin,
        args, context, pos_start, pos_end
    )

def execute_sqrt(args, context, pos_start, pos_end):
    return execute_numpy_ufunc(
        np.sqrt,
        args, context, pos_start, pos_end
    )

def execute_tan(args, context, pos_start, pos_end):
    return execute_numpy_ufunc(
        np.tan,
        args, context, pos_start, pos_end
    )


def execute_object_new(args, context, pos_start, pos_end):
    args = normalize_args(args, 0, context, pos_start, pos_end)
    return Object(object_object), None

def execute_object_getPrototype(args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)
    result = args[0].prototype
    if result == None:
        return Nil(), None

    return args[0].prototype, None

def execute_object_hashCode(args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)
    return Int(hash(args[0].uuid)), None

def execute_object_setPrototype(args, context, pos_start, pos_end):
    args = normalize_args(args, 2, context, pos_start, pos_end)
    if (not isPrototypeOf(args[0], args[1])) and args[0].uuid != args[1].uuid:
        args[0].prototype = args[1]
    else:
        return None, RTError(
            pos_start, pos_end,
            'cyclic prototype',
            context
        )
    
    return args[0], None

def execute_object_toBool(args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)    
    return Bool(args[0].is_true()), None

def execute_object_toString(args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)    
    return String(repr(args[0])), None

def execute_nil_new(args, context, pos_start, pos_end):
    args = normalize_args(args, 0, context, pos_start, pos_end)
    return Nil(), None


def execute_int_new(args, context, pos_start, pos_end):
    args = normalize_args(args, 0, context, pos_start, pos_end)
    return Int(0), None

def execute_int_toInt(args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)
    if not isinstance(args[0], Int):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not an integer',
            context
        )

    return args[0], None

def execute_int_toFloat(args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)
    if not isinstance(args[0], Int):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not an integer',
            context
        )

    return Float(float(args[0].value)), None

def execute_float_new(args, context, pos_start, pos_end):
    args = normalize_args(args, 0, context, pos_start, pos_end)
    return Float(0.0), None

def execute_float_toInt(args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)
    if not isinstance(args[0], Float):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a float',
            context
        )

    return Int(np.int64(args[0].value)), None

def execute_float_toFloat(args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)
    if not isinstance(args[0], Float):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a float',
            context
        )

    return args[0], None


def execute_bool_new(args, context, pos_start, pos_end):
    args = normalize_args(args, 0, context, pos_start, pos_end)
    return Bool(False), None


def execute_string_new(args, context, pos_start, pos_end):
    args = normalize_args(args, 0, context, pos_start, pos_end)
    return String(''), None

def execute_string_charAt(args, context, pos_start, pos_end):
    args = normalize_args(args, 2, context, pos_start, pos_end)
    if not isinstance(args[0], String):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a string',
            context
        )
        
    if not isinstance(args[1], Int):
        return None, RTError(
            args[1].pos_start, args[1].pos_end,
            f'{args[1]} is not an integer',
            context
        )
    
    result = args[0].value[args[1].value] if args[1].value < len(args[0].value) else ''
    return String(result), None

def execute_string_compareTo(args, context, pos_start, pos_end):
    args = normalize_args(args, 2, context, pos_start, pos_end)
    if not isinstance(args[0], String):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a string',
            context
        )

    if not isinstance(args[1], String):
        return None, RTError(
            args[1].pos_start, args[1].pos_end,
            f'{args[1]} is not a string',
            context
        )
        
        
    result = -1 if args[0].value < args[1].value else (0 if args[0].value == args[1].value else 1)
    return Int(result), None

def execute_string_concat(args, context, pos_start, pos_end):
    args = normalize_args(args, 2, context, pos_start, pos_end)
    if not isinstance(args[0], String):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a string',
            context
        )

    if not isinstance(args[1], String):
        return None, RTError(
            args[1].pos_start, args[1].pos_end,
            f'{args[1]} is not a string',
            context
        )
        
    return args[0].added_to(args[1])

def execute_string_endsWith(args, context, pos_start, pos_end):
    args = normalize_args(args, 2, context, pos_start, pos_end)
    if not isinstance(args[0], String):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a string',
            context
        )

    if not isinstance(args[1], String):
        return None, RTError(
            args[1].pos_start, args[1].pos_end,
            f'{args[1]} is not a string',
            context
        )
        
    return Bool(args[0].value.endswith(args[1].value)), None

def execute_string_indexOf(args, context, pos_start, pos_end):
    args = normalize_args(args, 2, context, pos_start, pos_end)
    if not isinstance(args[0], String):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a string',
            context
        )

    if not isinstance(args[1], String):
        return None, RTError(
            args[1].pos_start, args[1].pos_end,
            f'{args[1]} is not a string',
            context
        )
        
    try:
        return Int(args[0].value.index(args[1].value)), None
    except(ValueError):
        return Int(-1), None

def execute_string_lastIndexOf(args, context, pos_start, pos_end):
    args = normalize_args(args, 2, context, pos_start, pos_end)
    if not isinstance(args[0], String):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a string',
            context
        )

    if not isinstance(args[1], String):
        return None, RTError(
            args[1].pos_start, args[1].pos_end,
            f'{args[1]} is not a string',
            context
        )
        
    try:
        return Int(args[0].value.rindex(args[1].value)), None
    except(ValueError):
        return Int(-1), None

def execute_string_length(args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)
    if not isinstance(args[0], String):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a string',
            context
        )

    return Int(len(args[0].value)), None

def execute_string_replace(args, context, pos_start, pos_end):
    args = normalize_args(args, 3, context, pos_start, pos_end)
    if not isinstance(args[0], String):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a string',
            context
        )

    if not isinstance(args[1], String):
        return None, RTError(
            args[1].pos_start, args[1].pos_end,
            f'{args[1]} is not a string',
            context
        )
    
    if not isinstance(args[2], String):
        return None, RTError(
            args[2].pos_start, args[2].pos_end,
            f'{args[2]} is not a string',
            context
        )

    return String(args[0].value.replace(args[1].value, args[2].value)), None

def execute_string_startsWith(args, context, pos_start, pos_end):
    args = normalize_args(args, 2, context, pos_start, pos_end)
    if not isinstance(args[0], String):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a string',
            context
        )

    if not isinstance(args[1], String):
        return None, RTError(
            args[1].pos_start, args[1].pos_end,
            f'{args[1]} is not a string',
            context
        )
    
    return Bool(args[0].value.startswith(args[1].value)), None

def execute_string_substring(args, context, pos_start, pos_end):
    args = normalize_args(args, 3, context, pos_start, pos_end)
    if not isinstance(args[0], String):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a string',
            context
        )

    if not isinstance(args[1], Int):
        return None, RTError(
            args[1].pos_start, args[1].pos_end,
            f'{args[1]} is not an integer',
            context
        )
    
    if isinstance(args[2], Nil):
        return String(args[0].value[args[1].value:]), None
    else:
        if not isinstance(args[2], Int):
            return None, RTError(
                args[2].pos_start, args[2].pos_end,
                f'{args[2]} is not an integer',
                context
            )
        
        return String(args[0].value[args[1].value:args[2].value]), None

def execute_string_toCharList(args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)
    if not isinstance(args[0], String):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a string',
            context
        )

    return List(list(args[0].value)), None

def execute_string_toFloat(args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)
    if not isinstance(args[0], String):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a string',
            context
        )

    try:
        return Float(float(args[0].value)), None
    except:
        return None, RTError(
            pos_start, pos_end,
            f'could not convert {args[0]} to a float',
            context
        )

def execute_string_toInt(args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)
    if not isinstance(args[0], String):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a string',
            context
        )

    try:
        return Int(int(args[0].value)), None
    except:
        return None, RTError(
            pos_start, pos_end,
            f'could not convert {args[0]} to an integer',
            context
        )

def execute_string_toLowerCase(args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)
    if not isinstance(args[0], String):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a string',
            context
        )

    return String(args[0].value.lower()), None

def execute_string_toUpperCase(args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)
    if not isinstance(args[0], String):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a string',
            context
        )

    return String(args[0].value.upper()), None


def execute_list_new(args, context, pos_start, pos_end):
    args = normalize_args(args, 0, context, pos_start, pos_end)
    return List([]), None

def execute_list_add(args, context, pos_start, pos_end):
    args = normalize_args(args, 2, context, pos_start, pos_end)
    if not isinstance(args[0], List):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a list',
            context
        )

    args[0].set(repr(len(args[0].to_python_list())), args[1])
    return Nil(), None

def execute_list_clear(args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)
    if not isinstance(args[0], List):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a list',
            context
        )

    for i in range(0, len(args[0].to_python_list())):
        args[0].remove(repr(i))

    return Nil(), None

def execute_list_concat(args, context, pos_start, pos_end):
    args = normalize_args(args, 2, context, pos_start, pos_end)
    if not isinstance(args[0], List):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a list',
            context
        )

    if not isinstance(args[1], List):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[1]} is not a list',
            context
        )

    return args[0].added_to(args[1]), None

def execute_list_contains(args, context, pos_start, pos_end):
    args = normalize_args(args, 2, context, pos_start, pos_end)
    if not isinstance(args[0], List):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a list',
            context
        )

    for i in range(0, len(args[0].to_python_list())):
        result, error = args[0].get(repr(i)).get_comparison_eq(args[1])
        if error: return None, error
        
        if result.is_true(): return Bool(True), None

    return Bool(False), None

def execute_list_indexOf(args, context, pos_start, pos_end):
    args = normalize_args(args, 2, context, pos_start, pos_end)
    if not isinstance(args[0], List):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a list',
            context
        )

    for i in range(0, len(args[0].to_python_list())):
        result, error = args[0].get(repr(i)).get_comparison_eq(args[1])
        if error: return None, error
        
        if result.is_true(): return Int(i), None

    return Int(-1), None

def execute_list_isEmpty(args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)
    if not isinstance(args[0], List):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a list',
            context
        )

    return Bool(len(args[0].to_python_list()) == 0), None

def execute_list_lastIndexOf(args, context, pos_start, pos_end):
    args = normalize_args(args, 2, context, pos_start, pos_end)
    if not isinstance(args[0], List):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a list',
            context
        )

    i = len(args[0].to_python_list()) - 1
    while i >= 0:
        result, error = args[0].get(repr(i)).get_comparison_eq(args[1])
        if error: return None, error
        
        if result.is_true(): return Int(i), None
        i -= 1

    return Int(-1), None

def execute_list_length(args, context, pos_start, pos_end):
    args = normalize_args(args, 1, context, pos_start, pos_end)
    if not isinstance(args[0], List):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a list',
            context
        )

    return Int(len(args[0])), None

def execute_list_remove(args, context, pos_start, pos_end):
    args = normalize_args(args, 2, context, pos_start, pos_end)
    if not isinstance(args[0], List):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a list',
            context
        )
    
    if not isinstance(args[1], Int):
        return None, RTError(
            args[1].pos_start, args[1].pos_end,
            f'{args[1]} is not an integer',
            context
        )

    new_list = List([])
    idx = 0

    for i in range(0, len(args[0].to_python_list())):
        if i != args[1].value:
            new_list.set(repr(idx), args[0].get(repr(i)))
            idx += 1
        

    for i in range(0, len(args[0].to_python_list())):
        args[0].remove(repr(i))

    for i in range(0, len(new_list.to_python_list())):
        args[0].set(repr(i), new_list.get(repr(i)))
    

    return Nil(), None

def execute_list_subList(args, context, pos_start, pos_end):
    args = normalize_args(args, 3, context, pos_start, pos_end)
    if not isinstance(args[0], List):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a list',
            context
        )
    
    if not isinstance(args[1], Int):
        return None, RTError(
            args[1].pos_start, args[1].pos_end,
            f'{args[1]} is not an integer',
            context
        )

    if isinstance(args[2], Nil):
        return List(args[0].value[args[1].value:]), None
    else:
        if not isinstance(args[2], Int):
            return None, RTError(
                args[2].pos_start, args[2].pos_end,
                f'{args[2]} is not an integer',
                context
            )
        
        return List(args[0].value[args[1].value:args[2].value]), None

def execute_list_transform(args, context, pos_start, pos_end):
    args = normalize_args(args, 2, context, pos_start, pos_end)
    if not isinstance(args[0], List):
        return None, RTError(
            args[0].pos_start, args[0].pos_end,
            f'{args[0]} is not a list',
            context
        )
    
    if not isinstance(args[1], Function):
        return None, RTError(
            args[1].pos_start, args[1].pos_end,
            f'{args[1]} is not a function',
            context
        )

    new_list = List([])
    for i in range(0, len(args[0].to_python_list())):
        result, error = args[1].execute([args[0].get(repr(i))], context, pos_start, pos_end)
        if error: return None, error
        new_list.set(repr(i), result)
        
    return new_list, None

               
def execute_function_new(args, context, pos_start, pos_end):
    args = normalize_args(args, 0, context, pos_start, pos_end)
    return Function(
        '<anonymous>',
        lambda args, context, pos_start, pos_end: (Nil(), None)
    ), None

global_symbol_table.object.set('E', Float(math.e))
global_symbol_table.object.set('PI', Float(math.pi))

global_symbol_table.object.set('abs', Function('abs', execute_abs))
global_symbol_table.object.set('acos', Function('acos', execute_acos))
global_symbol_table.object.set('asin', Function('asin', execute_asin))
global_symbol_table.object.set('atan', Function('atan', execute_atan))
global_symbol_table.object.set('atan2', Function('atan2', execute_atan2))
global_symbol_table.object.set('ceil', Function('ceil', execute_ceil))
global_symbol_table.object.set('cos', Function('cos', execute_cos))
global_symbol_table.object.set('exp', Function('exp', execute_exp))
global_symbol_table.object.set('floor', Function('floor', execute_floor))
global_symbol_table.object.set('log', Function('log', execute_log))
global_symbol_table.object.set('max', Function('max', execute_max))
global_symbol_table.object.set('min', Function('min', execute_min))
global_symbol_table.object.set('pow', Function('pow', execute_pow))
global_symbol_table.object.set('print', Function('print', execute_print))
global_symbol_table.object.set('println', Function('println', execute_println))
global_symbol_table.object.set('random', Function('random', execute_random))
global_symbol_table.object.set('round', Function('round', execute_round))
global_symbol_table.object.set('sin', Function('sin', execute_sin))
global_symbol_table.object.set('sqrt', Function('sqrt', execute_sqrt))
global_symbol_table.object.set('tan', Function('tan', execute_tan))

global_symbol_table.object.set('Object', object_object)
global_symbol_table.object.set('Nil', nil_object)
global_symbol_table.object.set('Int', int_object)
global_symbol_table.object.set('Float', float_object)
global_symbol_table.object.set('Bool', bool_object)
global_symbol_table.object.set('String', string_object)
global_symbol_table.object.set('List', list_object)
global_symbol_table.object.set('Function', function_object)

object_object.set('new', Function('new', execute_object_new))
object_object.set('getPrototype', Function('getPrototype', execute_object_getPrototype, True))
object_object.set('hashCode', Function('hashCode', execute_object_hashCode, True))
object_object.set('setPrototype', Function('setPrototype', execute_object_setPrototype, True))
object_object.set('toBool', Function('toBool', execute_object_toBool, True))
object_object.set('toString', Function('toString', execute_object_toString, True))

nil_object.set('new', Function('new', execute_nil_new))

int_object.set('new', Function('new', execute_int_new))
int_object.set('MIN_VALUE', Int(-9223372036854775808))
int_object.set('MAX_VALUE', Int(9223372036854775807))
int_object.set('toFloat', Function('toFloat', execute_int_toFloat, True))
int_object.set('toInt', Function('toInt', execute_int_toInt, True))

float_object.set('new', Function('new', execute_float_new))
float_object.set('MIN_VALUE', Float(sys.float_info.min * sys.float_info.epsilon))
float_object.set('MAX_VALUE', Float(sys.float_info.max))
float_object.set('toFloat', Function('toFloat', execute_float_toFloat, True))
float_object.set('toInt', Function('toInt', execute_float_toInt, True))

bool_object.set('new', Function('new', execute_bool_new))

string_object.set('new', Function('new', execute_string_new))
string_object.set('charAt', Function('charAt', execute_string_charAt, True))
string_object.set('compareTo', Function('compareTo', execute_string_compareTo, True))
string_object.set('concat', Function('concat', execute_string_concat, True))
string_object.set('endsWith', Function('endsWith', execute_string_endsWith, True))
string_object.set('indexOf', Function('indexOf', execute_string_indexOf, True))
string_object.set('lastIndexOf', Function('lastIndexOf', execute_string_indexOf, True))
string_object.set('length', Function('length', execute_string_length, True))
string_object.set('replace', Function('replace', execute_string_replace, True))
string_object.set('startsWith', Function('startsWith', execute_string_startsWith, True))
string_object.set('substring', Function('substring', execute_string_substring, True))
string_object.set('toCharList', Function('toCharList', execute_string_toCharList, True))
string_object.set('toFloat', Function('toFloat', execute_string_toFloat, True))
string_object.set('toInt', Function('toInt', execute_string_toInt, True))
string_object.set('toLowerCase', Function('toLowerCase', execute_string_toLowerCase, True))
string_object.set('toUpperCase', Function('toUpperCase', execute_string_toUpperCase, True))

list_object.set('new', Function('new', execute_list_new))
list_object.set('add', Function('add', execute_list_add, True))
list_object.set('clear', Function('clear', execute_list_clear, True))
list_object.set('concat', Function('concat', execute_list_concat, True))
list_object.set('contains', Function('contains', execute_list_contains, True))
list_object.set('indexOf', Function('indexOf', execute_list_indexOf, True))
list_object.set('isEmpty', Function('isEmpty', execute_list_isEmpty, True))
list_object.set('lastIndexOf', Function('lastIndexOf', execute_list_lastIndexOf, True))
list_object.set('length', Function('length', execute_list_length, True))
list_object.set('remove', Function('remove', execute_list_remove, True))
list_object.set('subList', Function('subList', execute_list_subList, True))
list_object.set('transform', Function('transform', execute_list_transform, True))

function_object.set('new', Function('new', execute_function_new))

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
    f = open(fn, 'r')
    result, error = runstring(f.read(), fn)
    if error: print(error)
    return result, error