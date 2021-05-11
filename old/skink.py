#########################################
# IMPORTS
#########################################
import numpy as np
import math
import json
# import inspect
# import struct
import string
from strings_with_arrows import *
# import copy

#########################################
# CONSTANTS
#########################################
DIGITS = '0123456789'
INT_LIMIT = 2**32
LONG_LIMIT = 2**64
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS+DIGITS
def isFunction(obj):
        return hasattr(obj, '__call__')

# myNull = None

def arg_length(fn):
        return fn.__code__.co_argcount


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



class PythonError(RTError):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start,pos_end,details,context)
        self.context = context
        self.error_name = 'Python Error'
        
        
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
TT_STRING = 'STRING'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_LSQUARE = 'LSQUARE'
TT_RSQUARE = 'RSQUARE'
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
TT_COMMA = 'COMMA'
TT_DOT = 'DOT'
TT_NEWLINE = 'NEWLINE'
# TT_LANGLE = 'LANGLE'
# TT_RANGLE = 'RANGLE'
# TT_ARROW = 'ARROW'

KEYWORDS = [
        'and',
        'or',
        'not',
        'if',
        'elif',
        'else',
        'while',
        'namespace',
        'return',
        'continue',
        'break'
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
                elif self.current_char in ';\n':
                        tokens.append(Token(TT_NEWLINE,pos_start=self.pos))
                        self.advance()
                elif self.current_char in DIGITS:
                        tokens.append(self.make_number())
                elif self.current_char in LETTERS:
                        tokens.append(self.make_identifier())
                elif self.current_char == '"':
                        tokens.append(self.make_string())
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
                elif self.current_char == '[':
                        tokens.append(Token(TT_LSQUARE, pos_start=self.pos))
                        self.advance()
                elif self.current_char == ']':
                        tokens.append(Token(TT_RSQUARE, pos_start=self.pos))
                        self.advance()
                elif self.current_char == '.':
                        tokens.append(Token(TT_DOT, pos_start=self.pos))
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
                elif self.current_char == ',':
                        tokens.append(Token(TT_COMMA, pos_start=self.pos))
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
                    return Token(TT_INT, np.int32(math.fmod(float(num_str),2**32)),pos_start,self.pos)
            elif l_count == 1:
                    return Token(TT_LONG, np.int64(math.fmod(float(num_str),2**64)),pos_start,self.pos)
            else:
                    return Token(TT_DOUBLE, float(num_str), pos_start, self.pos)

    def make_string(self):
                string = ''
                pos_start = self.pos.copy()
                escape_character = False
                self.advance()

                escape_characters = {
                        'n': '\n',
                        't': '\t',
                        '"': '"',
                        '\\': '\\'
                }

                while self.current_char != None and (self.current_char != '"' or escape_character):
                        if escape_character:
                                string += escape_characters.get(self.current_char, self.current_char)
                                escape_character = False
                        else:
                                if self.current_char == '\\':
                                        escape_character = True
                                else:
                                        string += self.current_char
                                        escape_character = False
                        self.advance()
		
                self.advance()
                # print(string)

                return Token(TT_STRING, string, pos_start, self.pos)

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
#     def make_minus_or_arrow(self):
#                 tok_type = TT_MINUS
#                 pos_start = self.pos.copy()

#                 self.advance()
#                 if self.current_char == '>':
#                         self.advance()
#                         tok_type = TT_ARROW
#                 return Token(tok_type, pos_start, self.pos)

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

class StringNode:
        def __init__(self,tok):
                self.tok = tok
                self.pos_start = self.tok.pos_start
                self.pos_end = self.tok.pos_end
        def __repr__(self):
                return f'{self.tok}'

class ListNode:
        def __init__(self, element_nodes, pos_start, pos_end):
                self.element_nodes = element_nodes
                self.pos_start = pos_start
                self.pos_end = pos_end

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

class IfNode:
	def __init__(self, cases, else_case):
		self.cases = cases
		self.else_case = else_case

		self.pos_start = self.cases[0][0].pos_start
		self.pos_end = (self.else_case or self.cases[len(self.cases) - 1][0]).pos_end

class WhileNode:
        def __init__(self,condition_node,body_node):
                self.condition_node = condition_node
                self.body_node = body_node

                self.pos_start = self.condition_node.pos_start
                self.pos_end = self.body_node.pos_end

                self.pos_end = self.body_node.pos_end

class NamespaceNode:
        def __init__(self,var_name_tok,body_node,pos_end):
                self.var_name_tok = var_name_tok
                self.body_node = body_node

                self.pos_start = self.var_name_tok.pos_start
                self.pos_end = pos_end

# class ArrayTypeNode:
#         def __init__(self,base_type):
#                 self.base_type = base_type

class KeyNode:
        def __init__(self,obj_node,key_node):
                self.obj_node = obj_node
                self.key_node = key_node

                self.pos_start = self.obj_node.pos_start
                self.pos_end = self.key_node.pos_end

class FuncDefNode:
        def __init__(self,type_tok,var_name_tok, arg_name_toks, body_node,  should_auto_return):
                self.type_tok = type_tok
                self.var_name_tok = var_name_tok
                self.arg_name_toks = arg_name_toks
                self.body_node = body_node

                self.should_auto_return = should_auto_return
                self.pos_start = self.type_tok.pos_start
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
class ReturnNode:
  def __init__(self, node_to_return, pos_start, pos_end):
    self.node_to_return = node_to_return

    self.pos_start = pos_start
    self.pos_end = pos_end

class ContinueNode:
  def __init__(self, pos_start, pos_end):
    self.pos_start = pos_start
    self.pos_end = pos_end

class BreakNode:
  def __init__(self, pos_start, pos_end):
    self.pos_start = pos_start
    self.pos_end = pos_end


#########################################
# PARSE RESULT
#########################################
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

  def register_unadvancement(self):
              self.advance_count -= 1

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
                self.update_current_tok()
                return self.current_tok
        
        def reverse(self,amount=1):
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
                                'Expected "+", "-", "*", "/", "^", "==", "!=", "{", ">", <=", ">=", "and" or "or"'
                        ))
                return res
        
        def if_expr(self):
                res = ParseResult()
                all_cases = res.register(self.if_expr_cases('if'))
                # print(res.error.as_string())
                if res.error: return res
                cases, else_case = all_cases
                # res.register_advancement()
                # self.advance()
                return res.success(IfNode(cases, else_case))
        

        def namespace_expr(self):
                res = ParseResult()
                if not self.current_tok.matches(TT_KEYWORD,'namespace'):
                        return res.failure(InvalidSyntaxError(
                                self.current_tok.pos_start, self.current_tok.pos_end,
                                'Expected "namespace"'  
                        ))
                
                res.register_advancement()
                self.advance()
                if self.current_tok.type != TT_IDENTIFIER:
                        return res.failure(InvalidSyntaxError(
                                self.current_tok.pos_start, self.current_tok.pos_end,
                                'Expected identifier'
                        ))  

                var_name_tok = self.current_tok
                if res.error: return res

                if self.current_tok != TT_LCURLY:
                        res.register_advancement()
                        self.advance()   

                if not self.current_tok.type == TT_LCURLY:
                        # print("nuh uh")
                        return res.failure(InvalidSyntaxError(
                                self.current_tok.pos_start, self.current_tok.pos_end,
                                'Expected "{"'
                        ))
                        

                res.register_advancement()
                self.advance()
                body = res.register(self.statements())
                # res.register_advancement()
                # self.advance()
                if not self.current_tok.type == TT_RCURLY:
                        # print("nuh uh")
                        return res.failure(InvalidSyntaxError(
                                self.current_tok.pos_start, self.current_tok.pos_end,
                                'Expected "}"'
                        ))
                res.register_advancement()
                self.advance()

                # if body == None: body = VarAccessNode(Token(TT_IDENTIFIER,"null",pos_start=node.pos_start))
                return res.success(NamespaceNode(var_name_tok,body,self.current_tok.pos_end))


        def if_expr_cases(self, case_keyword):
                res = ParseResult()
                cases = []
                else_case = None

                if not self.current_tok.matches(TT_KEYWORD, case_keyword):
                        return res.failure(InvalidSyntaxError(
                                self.current_tok.pos_start, self.current_tok.pos_end,
                                f'Expected "{case_keyword}"'
                        ))
                
                res.register_advancement()
                self.advance()
                
                condition = res.register(self.expr())
                if res.error: return res
                if not self.current_tok.type == TT_LCURLY:
                        return res.failure(InvalidSyntaxError(
                                self.current_tok.pos_start, self.current_tok.pos_end,
                                'Expected "{"'
                        ))
                
                while self.current_tok != None and self.current_tok.type == TT_NEWLINE:
                        res.register_advancement()
                        self.advance()
                
                res.register_advancement()
                self.advance()

                statements = res.register(self.statements())
                if res.error: return res
                cases.append((condition, statements))

                all_cases = res.register(self.if_expr_b_or_c())
                if res.error: return res
                new_cases, else_case = all_cases
                cases.extend(new_cases)
                if not self.current_tok.type == TT_RCURLY:
                        return res.failure(InvalidSyntaxError(
                                self.current_tok.pos_start, self.current_tok.pos_end,
                                'Expected "}"'
                        ))
                
                
                res.register_advancement()
                self.advance()
                
                if self.current_tok.type != TT_EOF:
                        all_cases = res.register(self.if_expr_b_or_c())
                        if res.error: return res
                        new_cases, else_case = all_cases
                        cases.extend(new_cases)
                        

                return res.success((cases,else_case))                   

                
        def if_expr_b(self):
                # print("good!")
                return self.if_expr_cases("elif")
        
        def if_expr_c(self):
                res = ParseResult()
                else_case = None
                
                if self.current_tok.matches(TT_KEYWORD, 'else'):
                        res.register_advancement()
                        self.advance()
                        if self.current_tok.type == TT_NEWLINE:
                                statements = res.register(self.statements())
                                if res.error: return res
                                else_case = (statements, True)
                                
                                if self.current_tok.type == TT_RCURLY:
                                        res.register_advancement()
                                        self.advance()
                                else:
                                        return res.failure(InvalidSyntaxError(
                                                self.current_tok.pos_start, self.current_tok.pos_end,
                                                'Expected "}"'
                                        ))
                        else:
                                statement = res.register(self.statement())
                                if res.error: return res
                                else_case = statement
                return res.success(else_case)

        def if_expr_b_or_c(self):
                res = ParseResult()
                cases, else_case = [], None

                if self.current_tok.matches(TT_KEYWORD, 'elif'):
                        all_cases = res.register(self.if_expr_b())
                        if res.error: return res
                        cases, else_case = all_cases
                else:
                        else_case = res.register(self.if_expr_c())
                        if res.error: return res
                
                return res.success((cases, else_case))

        # def if_expr(self):
        #         res = ParseResult()
        #         cases = []
        #         else_case = None

        #         if not self.current_tok.matches(TT_KEYWORD,"if"):
        #                 return res.failure(InvalidSyntaxError(
        #                         self.current_tok.pos_start, self.current_tok.pos_end,
        #                         'Expected "if"'
        #                 ))

        #         res.register_advancement()
        #         self.advance()
        #         condition = res.register(self.expr())
        #         if res.error: return res
        #         if not self.current_tok.type == TT_LCURLY:
        #                 # print("nuh uh")
        #                 return res.failure(InvalidSyntaxError(
        #                         self.current_tok.pos_start, self.current_tok.pos_end,
        #                         'Expected "{"'
        #                 ))
        #         res.register_advancement()
        #         self.advance()
        #         expr = res.register(self.expr())
        #         if res.error: return res

        #         # res.register_advancement()
        #         self.advance()
        #         if not self.current_tok.type == TT_RCURLY:
        #                 # print("nuh uh")
        #                 return res.failure(InvalidSyntaxError(
        #                         self.current_tok.pos_start, self.current_tok.pos_end,
        #                         'Expected "}"'
        #                 ))
                
        
        #         cases.append((condition,expr))
        #         i = 0
        #         res.register_advancement()
        #         self.advance()
        #         # print("YES! YES!!1")
        #         # print(self.current_tok
        #         # print(self.current_tok.matches(TT_KEYWORD,"else") 
        #         #      ,get(self.tokens,self.tok_idx+1).matches(TT_KEYWORD,"if") )
        #         while(self.current_tok.matches(TT_KEYWORD,"else") 
        #              and get(self.tokens,self.tok_idx+1)
        #              and get(self.tokens,self.tok_idx+1).matches(TT_KEYWORD,"if")):
        #                 i += 1
        #                 res.register_advancement()
        #                 self.advance()
        #                 res.register_advancement()
        #                 self.advance()
        #                 condition = res.register(self.expr())
        #                 if res.error: return res
        #                 if not self.current_tok.type == TT_LCURLY:
        #                         # print("nuh uh")
        #                         return res.failure(InvalidSyntaxError(
        #                                 self.current_tok.pos_start, self.current_tok.pos_end,
        #                                 'Expected "{"'
        #                         ))
        #                 res.register_advancement()
        #                 self.advance()
        #                 expr = res.register(self.expr())
        #                 if res.error: return res

        #                 # # res.register_advancement()
        #                 # self.advance()
        #                 if not self.current_tok.type == TT_RCURLY:
        #                         # print("nuh uh")
        #                         return res.failure(InvalidSyntaxError(
        #                                 self.current_tok.pos_start, self.current_tok.pos_end,
        #                                 'Expected "}"'
        #                         ))
                        
                
        #                 cases.append((condition,expr))


        #                 # cases.append((None))

        #         if i > 0:
        #                 res.register_advancement()
        #                 self.advance()

        #         if self.current_tok.matches(TT_KEYWORD, 'else'):
        #                 res.register_advancement()
        #                 self.advance()
        #                 if not self.current_tok.type == TT_LCURLY:
        #                         return res.failure(InvalidSyntaxError(
        #                                 self.current_tok.pos_start, self.current_tok.pos_end,
        #                                 'Expected "{"'
        #                         ))
        #                 res.register_advancement()
        #                 self.advance()
        #                 expr = res.register(self.expr())
        #                 if res.error: return res

        #                 # res.register_advancement()
        #                 self.advance()
        #                 if not self.current_tok.type == TT_RCURLY:
        #                         # print("nuh uh")
        #                         return res.failure(InvalidSyntaxError(
        #                                 self.current_tok.pos_start, self.current_tok.pos_end,
        #                                 'Expected "}"'
        #                         ))
                        
        #                 else_case = expr

                        
        #         res.register_advancement()
        #         self.advance()
        #         # print("HUH?????")
        #         return res.success(IfNode(cases, else_case))

        
        def func_def(self):
                res = ParseResult()
                if self.current_tok.type != TT_IDENTIFIER:
                        return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        'Expected identifier'
                        ))
                
                type_tok = self.current_tok
                res.register_advancement()
                self.advance()
                if self.current_tok.type != TT_IDENTIFIER:
                        return res.failure(InvalidSyntaxError(
                                self.current_tok.pos_start, self.current_tok.pos_end,
                                'Expected identifier'
                        ))
                var_name_tok = self.current_tok
                res.register_advancement()
                self.advance()
                if self.current_tok.type != TT_LPAREN:
                        return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        'Expected "("'
                        ))

                res.register_advancement()
                self.advance()
                arg_name_toks = []
                # body_node = None
                
                        # in dynamic language: arg_name_toks = ["a","b","c"...]
                        # in static language: arg_name_toks = [("int",a)...]
                if self.current_tok.type == TT_IDENTIFIER:
                        if self.current_tok.type != TT_IDENTIFIER:
                                        return res.failure(InvalidSyntaxError(
                                        self.current_tok.pos_start, self.current_tok.pos_end,
                                        f"Expected identifier"
                                ))
                        
                        t1 = self.current_tok #int
                        res.register_advancement()
                        self.advance()
                        if self.current_tok.type != TT_IDENTIFIER:
                                        return res.failure(InvalidSyntaxError(
                                        self.current_tok.pos_start, self.current_tok.pos_end,
                                        f"Expected identifier"
                                ))
                        # 
                        t2 = self.current_tok
                        res.register_advancement()
                        self.advance()
                        arg_name_toks.append((t1,t2))
                        # 
                        # print("BruteForce1",arg_name_toks)
                        i = 0
                        # print(self.current_tok.type != TT_RPAREN)
                        if self.current_tok.type != TT_RPAREN: 
                                while self.current_tok.type == TT_COMMA:
                                        # i += 1
                                        res.register_advancement()
                                        self.advance()
                                        if self.current_tok.type != TT_IDENTIFIER:
                                                return res.failure(InvalidSyntaxError(
                                                self.current_tok.pos_start, self.current_tok.pos_end,
                                                f"Expected identifier"
                                        ))
                                        t1 = self.current_tok #int
                                        res.register_advancement()
                                        self.advance()
                                        if self.current_tok.type != TT_IDENTIFIER:
                                                return res.failure(InvalidSyntaxError(
                                                self.current_tok.pos_start, self.current_tok.pos_end,
                                                f"Expected identifier"
                                        ))
                                        t2 = self.current_tok
                                        res.register_advancement()
                                        self.advance()
                                        arg_name_toks.append((t1,t2))
                                        # print({'i':i,'t1':t1,'t2':t2})
                                        i += 1
                        # print("NewBrute0")
                        # arg_name_toks.append(self.current_tok)
                        # print(arg_name_toks)
                        res.register_advancement()
                        self.advance()
                        while self.current_tok.type == TT_NEWLINE:
                                res.register_advancement()
                                self.advance()

                        if not self.current_tok.type == TT_LCURLY:
                                if self.current_tok.type == TT_EQ:
                                        res.register_advancement()
                                        self.advance()
                                        body = res.register(self.expr())
                                        return res.success(FuncDefNode(type_tok, var_name_tok, arg_name_toks, body, True))
                                else:
                                        return res.failure(InvalidSyntaxError(
                                                self.current_tok.pos_start, self.current_tok.pos_end,
                                                'Expected "{" or "="'
                                        ))
                                

                        res.register_advancement()
                        self.advance()
                        body = res.register(self.statements())
                        # res.register_advancement()
                        # self.advance()
                        if not self.current_tok.type == TT_RCURLY:
                                # print("nuh uh")
                                return res.failure(InvalidSyntaxError(
                                        self.current_tok.pos_start, self.current_tok.pos_end,
                                        'Expected "}"'
                                ))

                        # print(self.current_tok)
                                
                        res.register_advancement()
                        self.advance()

                        if res.error: return res
                        return res.success(FuncDefNode(type_tok, var_name_tok, arg_name_toks, body, False))
                else:
                                return res.failure(InvalidSyntaxError(
                                        self.current_tok.pos_start, self.current_tok.pos_end,
                                        'Expected identifier'
                                ))




        def key_expr(self):
                res = ParseResult()
                dot_expr = res.register(self.dot_expr())
                # arg_nodes = []
                if res.error: return res

                if self.current_tok.type == TT_LSQUARE:
                        res.register_advancement()
                        self.advance()
                        # if self.current_tok.type == TT_RSQUARE:
                        #         res.register_advancement()
                        # self.advance()
                        #         return res.success(ArrayTypeNode(call))
                        key = res.register(self.expr())
                        if res.error: return res
                        # res.register_advancement()
# self.advance()
                        # print(self.current_tok)
                        if self.current_tok.type != TT_RSQUARE:
                                return res.failure(InvalidSyntaxError(
                                        self.current_tok.pos_start, self.current_tok.pos_end,
                                        'Expected "]"'
                                ))
                        
                        res.register_advancement()
                        self.advance()
                        return res.success(KeyNode(dot_expr,key))
                return res.success(dot_expr)
   
        # def dot_expr(self):
        #         res = ParseResult()
        #         atom = res.register(self.atom())
        #         if res.error: return res
        #         if self.current_tok.type == TT_DOT:
        #                 res.register_advancement()
        #                 self.advance()
        #                 if self.current_tok.type != TT_IDENTIFIER:
        #                         return res.failure(InvalidSyntaxError(
        #                                 self.current_tok.pos_start, self.current_tok.pos_end,
        #                                 'Expected identifier'
        #                         ))
        #                 identifier = self.current_tok
        #                 res.register_advancement()
        #                 self.advance()
        #                 return res.success(KeyNode(atom,StringNode(identifier)))
        #         else:
        #                 return res.success(atom)

        def dot_expr(self):
                res = ParseResult()
                atom = res.register(self.atom())
                if res.error: return res
                while self.current_tok.type == TT_DOT:
                        res.register_advancement()
                        self.advance()
                        if self.current_tok.type != TT_IDENTIFIER:
                                return res.failure(InvalidSyntaxError(
                                        self.current_tok.pos_start, self.current_tok.pos_end,
                                        'Expected identifier'
                                ))
                        identifier = self.current_tok
                        res.register_advancement()
                        self.advance()
                        atom = KeyNode(atom,StringNode(identifier))
                return res.success(atom)

        def call(self):
                res = ParseResult()
                key_expr = res.register(self.key_expr())
                arg_nodes = []
                if res.error: return res

                if self.current_tok.type == TT_LPAREN:
                        res.register_advancement()
                        self.advance()
                        if self.current_tok.type == TT_RPAREN:
                                res.register_advancement()
                                self.advance()
                        else:
                                arg_nodes.append(res.register(self.expr()))
                                if res.error:
                                        return res.failure(InvalidSyntaxError(
                                        self.current_tok.pos_start, self.current_tok.pos_end,
                                        'Expected ")",  "if", "while" , int, long, double, identifier, "+", "-", "(" or "not"'
                                        ))

                                while self.current_tok.type == TT_COMMA:
                                        res.register_advancement()
                                        self.advance()

                                        arg_nodes.append(res.register(self.expr()))
                                        if res.error: return res

                                        if self.current_tok.type != TT_RPAREN:
                                                return res.failure(InvalidSyntaxError(
                                                self.current_tok.pos_start, self.current_tok.pos_end,
                                                f'Expected "," or ")"'
                                                ))

                                        res.register_advancement()
                                        self.advance()
                        if len(arg_nodes) == 1:
                                res.register_advancement()
                                self.advance()
                        # print(self.current_tok)
                        if self.tokens[self.tok_idx-1].type != TT_RPAREN:
                                                return res.failure(InvalidSyntaxError(
                                                self.current_tok.pos_start, self.current_tok.pos_end,
                                                f'Expected "," or ")"'
                                                ))
                        # while self.current_tok != TT_EOF and self.tok_idx < len(self.tokens):
                        #         res.register_advancement()
                                # self.advance()
                        # print(key_expr,arg_nodes,self.current_tok)
                        return res.success(CallNode(key_expr, arg_nodes))
                return res.success(key_expr)

        def list_expr(self):
                res = ParseResult()
                element_nodes = []
                pos_start = self.current_tok.pos_start
                if self.current_tok.type != TT_LCURLY:
                        return res.failure(InvalidSyntaxError(
                                self.current_tok.pos_start, self.current_tok.pos_end,
                                'Expected "{"'
                        ))
                res.register_advancement()
                self.advance()
                if self.current_tok.type == TT_RCURLY:
                        res.register_advancement()
                        self.advance()
                else:
                                element_nodes.append(res.register(self.expr()))
                                if res.error:
                                        return res.failure(InvalidSyntaxError(
                                        self.current_tok.pos_start, self.current_tok.pos_end,
                                        'Expected "}",  "if", "while" , int, long, double, identifier, "+", "-", "(" or "not"'
                                        ))

                                while self.current_tok.type == TT_COMMA:
                                        res.register_advancement()
                                        self.advance()

                                        element_nodes.append(res.register(self.expr()))
                                        if res.error: return res
                                
                                if self.current_tok.type != TT_RCURLY:
                                        return res.failure(InvalidSyntaxError(
                                                self.current_tok.pos_start, self.current_tok.pos_end,
                                                'Expected "," or "}"'
                                        ))
                                
                                res.register_advancement()
                                self.advance()
                                
                return res.success(ListNode(
                                element_nodes,
                                pos_start,
                                self.current_tok.pos_end.copy()
                        ))


        #########################################
        def atom(self): 
                res = ParseResult()
                tok = self.current_tok
                if tok.type in (TT_PLUS,TT_MINUS):
                        res.register_advancement()
                        self.advance()
                        atom = res.register(self.atom())
                        if res.error: return res 
                        return res.success(UnaryOpNode(tok, atom))
                elif tok.type in (TT_INT,TT_LONG,TT_DOUBLE):
                        res.register_advancement()
                        self.advance()
                        return res.success(NumberNode(tok))
                elif tok.matches(TT_KEYWORD,'namespace'):
                        namespace_expr = res.register(self.namespace_expr())
                        if res.error: return res
                        return res.success(namespace_expr)
                elif tok.type == TT_STRING:
                        res.register_advancement()
                        self.advance()
                        return res.success(StringNode(tok))
                elif tok.type == TT_IDENTIFIER and getattr(get(self.tokens,self.tok_idx+1),"type",None) != TT_IDENTIFIER:
                        temp = res.success(VarAccessNode(tok))
                        res.register_advancement()
                        self.advance()
                        return temp
                elif tok.type == TT_LCURLY:
                        list_expr = res.register(self.list_expr())
                        if res.error: return res
                        return res.success(list_expr)
                elif tok.matches(TT_KEYWORD,'if'):
                        # print("?")
                        if_expr = res.register(self.if_expr())
                        if res.error: return res
                        return res.success(if_expr)
                elif tok.matches(TT_KEYWORD,'while'):
                        while_expr = res.register(self.while_expr())
                        if res.error: return res
                        return res.success(while_expr)
                elif tok.matches(TT_KEYWORD,'while'):
                        while_expr = res.register(self.while_expr())
                        if res.error: return res
                        return res.success(while_expr)
                elif(tok.type == TT_IDENTIFIER
                     and get(self.tokens,self.tok_idx+1)
                     and get(self.tokens,self.tok_idx+1).type == TT_IDENTIFIER
                     and get(self.tokens,self.tok_idx+2)
                     and get(self.tokens,self.tok_idx+2).type == TT_LPAREN):
                        return self.func_def()
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
                                'Expected ")"'
                                ))
                else:
                        return res.failure(InvalidSyntaxError(
                                tok.pos_start, tok.pos_end,
                                'Expected int, long, double, identifier, "+", "-", "(", "{", "if", "for", or "while"'
                        ))
        
        def while_expr(self):
                res = ParseResult()
                if not self.current_tok.matches(TT_KEYWORD,'while'):
                        return res.failure(InvalidSyntaxError(
                                self.current_tok.pos_start, self.current_tok.pos_end,
                                'Expected "while"'  
                        ))
                
                res.register_advancement()
                self.advance()
                condition = res.register(self.expr())
                if res.error: return res
                
                if not self.current_tok.type == TT_LCURLY:
                        # print("nuh uh")
                        return res.failure(InvalidSyntaxError(
                                self.current_tok.pos_start, self.current_tok.pos_end,
                                'Expected "{"'
                        ))
                        

                res.register_advancement()
                self.advance()
                body = res.register(self.statements())
                # res.register_advancement()
                # self.advance()
                if not self.current_tok.type == TT_RCURLY:
                        # print("nuh uh")
                        return res.failure(InvalidSyntaxError(
                                self.current_tok.pos_start, self.current_tok.pos_end,
                                'Expected "}"'
                        ))
                res.register_advancement()
                self.advance()
                return res.success(WhileNode(condition,body))

        def term(self): 
                return self.bin_op(self.call, (TT_MUL,TT_DIV))

        def arith_expr(self):
                return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

        def comp_expr(self):
                res = ParseResult()

                if self.current_tok.matches(TT_KEYWORD, "not"):
                        op_tok = self.current_tok
                        res.register_advancement()
                        self.advance()

                        node = res.register(self.comp_expr())
                        if res.error: return res
                        return res.success(UnaryOpNode(op_tok, node))

                node = res.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))

                if res.error: return res
                        # return res.failure(InvalidSyntaxError(
                        #         self.current_tok.pos_start, self.current_tok.pos_end,
                        #         'Expected "if", "while", int, long, double, identifier, "+", "-", "(", "{" or "not"'
                        # ))

                return res.success(node)
        def expr(self): 
                res = ParseResult()
                temp = self.bin_op(self.comp_expr, ((TT_KEYWORD,"and"), (TT_KEYWORD,"or")))
                # print(self.current_tok)
                if(self.current_tok.type == TT_EQ):
                        # print("nish!")
                        res.register_unadvancement()
                        self.unadvance()
                        var_name_tok = self.current_tok

                        res.register_unadvancement()
                        self.unadvance()

                        # print(self.current_tok.type == TT_IDENTIFIER or self.current_tok.type == TT_LPAREN
                        #    ,get(self.tokens,self.tok_idx-1)
                        #    ,self.tokens[self.tok_idx-1].type == TT_IDENTIFIER)
                        if ((self.current_tok.type == TT_IDENTIFIER or self.current_tok.type == TT_LPAREN)
                           and get(self.tokens,self.tok_idx-1)
                           and self.tokens[self.tok_idx-1].type == TT_IDENTIFIER):
                                if self.current_tok.type == TT_LPAREN: 
                                        res.register(self.unadvance())
                                        res.register(self.unadvance())
                                if res.error: return res
                                # print("HUH?")
                                return self.func_def()
                        elif self.current_tok.type == TT_DOT:
                                res.register_unadvancement()
                                self.unadvance()
                                var_name_tok = res.register(self.dot_expr())
                                if res.error: return res
                        else:
                                res.register_advancement()
                                self.advance()
                                res.register_advancement()
                                self.advance()
                                
                        if self.current_tok.type != TT_EQ:
                                return res.failure(InvalidSyntaxError(
                                        self.current_tok.pos_start, self.current_tok.pos_end,
                                        'Expected "="'
                                ))  
                        res.register_advancement()
                        self.advance()
                        expr = res.register(self.expr())
                        if res.error: return res
                        return res.success(SetNode(var_name_tok,expr))

                if(self.current_tok.type == TT_IDENTIFIER 
                and get(self.tokens,self.tok_idx+1).type == TT_IDENTIFIER
                and get(self.tokens,self.tok_idx+2).type == TT_EQ):
                        type_node = self.current_tok
                        res.register_advancement()
                        self.advance()
                        # if self.current_tok.type == TT_EOF:
                        #         res.register(self.unadvance())
                        #         return self.atom()
                        if self.current_tok.type != TT_IDENTIFIER:
                                return res.failure(InvalidSyntaxError(
                                        self.current_tok.pos_start, self.current_tok.pos_end,
                                        "Expected identifier"
                                ))

                        var_name = self.current_tok
                        res.register_advancement()
                        self.advance()
                        if self.current_tok.type != TT_EQ:
                                return res.failure(InvalidSyntaxError(
                                        self.current_tok.pos_start, self.current_tok.pos_end,
                                        'Expected "="'
                                ))  
                        res.register_advancement()
                        self.advance()
                        expr = res.register(self.expr())
                        if res.error: return res
                        
                        # res.register_advancement()
                        # self.advance()
                        return res.success(VarAssignNode(var_name, expr, type_node))
                # if(self.current_tok.type == TT_LPAREN):
                #         return self.call() if temp.error else temp
                # print(temp.node,temp.error)
                return temp
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
        
        def statements(self):
                res = ParseResult()
                statements = []
                pos_start = self.current_tok.pos_start.copy()

                while self.current_tok.type == TT_NEWLINE:
                        res.register_advancement()
                        self.advance()

                statement = res.register(self.statement())
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
                        statement = res.try_register(self.statement())
                        if not statement:
                                self.reverse(res.to_reverse_count)
                                more_statements = False
                                continue
                        statements.append(statement)

                return res.success(ListNode(
                statements,
                pos_start,
                self.current_tok.pos_end.copy()
                ))

        def statement(self):
                        res = ParseResult()
                        pos_start = self.current_tok.pos_start.copy()

                        if self.current_tok.matches(TT_KEYWORD, 'return'):
                                res.register_advancement()
                                self.advance()
                                self.reverse(res.to_reverse_count)
                                expr = res.try_register(self.expr())
                                return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))
                

                        # expr = res.try_register(self.expr())
                        # if not expr:
                        #         self.reverse(res.to_reverse_count)
                        #         return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))
                        
                        if self.current_tok.matches(TT_KEYWORD, 'continue'):
                                res.register_advancement()
                                self.advance()
                                return res.success(ContinueNode(pos_start, self.current_tok.pos_start.copy()))
                        
                        if self.current_tok.matches(TT_KEYWORD, 'break'):
                                res.register_advancement()
                                self.advance()
                                return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))

                        expr = res.register(self.expr())
                        if res.error:
                                return res.failure(InvalidSyntaxError(
                                        self.current_tok.pos_start, self.current_tok.pos_end,
                                        'Expected "return", "continue", "break", "if", "while", "namespace", int, long, double, identifier, "+", "-", "(", "{" or "not"'
                                ))

                        return res.success(expr)

                        

#########################################
# RUNTIME RESULT
#########################################
class RTResult:
        def __init__(self):
                self.reset()

        def reset(self):
                self.value = None
                self.error = None
                self.func_return_value = None
                self.loop_should_continue = False
                self.loop_should_break = False


        def register(self, res):
                if res.error: self.error = res.error
                self.func_return_value = res.func_return_value
                self.loop_should_continue = res.loop_should_continue
                self.loop_should_break = res.loop_should_break
                return res.value

        def success(self, value):
                self.reset()
                self.value = value
                return self

        def success_return(self, value):
                self.reset()
                self.func_return_value = value
        
        def success_continue(self): 
                self.reset()
                self.loop_should_continue = True
        
        def success_break(self):
                self.reset()
                self.loop_should_break = True
                
        def should_return(self):
                return (
                        self.error or 
                        self.func_return_value or 
                        self.loop_should_continue or
                        self.loop_should_break
                )


        def failure(self, error):
                self.reset()
                self.error = error
                return self
        


#######################################
# SYMBOL TABLE
#######################################

class SymbolTable:
        def __init__(self, parent=None):
                self.symbols = {}
                self.parent = parent
                self._inherit = parent

        def inherit(self, otherTable):
                new_table = {}
                for key in otherTable.symbols:
                        if isFunction(otherTable.symbols[key]) and not getattr(otherTable.symbols[key],"_static",False):
                                def _(*args):
                                        return otherTable.symbols[key](self,*args)
                                new_table[key] = _
                        else:
                                new_table[key] = otherTable.symbols[key]
                new_table = SymbolTable(new_table)
                self.parent = new_table
                self._inherit = otherTable
                return new_table

        def get(self, name):
                value = self.symbols.get(name, None)
                if value == None and self.parent:
                        return self.parent.get(name)
                return value

        def set(self, name, value):
                self.symbols[name] = value

        def remove(self, name):
                del self.symbols[name]

        @staticmethod
        def fromSymbols(symbols):
                result = SymbolTable()
                result.symbols = symbols
                return result


#######################################
# VALUES
#######################################
a: int = 2
a = "a"
class Value(SymbolTable):
        def __init__(self):
                super().__init__()
                self.set_pos()
                self.set_context()

        def set_pos(self, pos_start=None, pos_end=None):
                self.pos_start = pos_start
                self.pos_end = pos_end
                return self

        def idx(self,index):
                t = self.get(index.get('value'))
                # print(t,(t,None))
                return (myNull, None) if t == None else (t, None)

        def set_context(self, context=None):
                self.context = context
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

        def notted(self, other):
                return None, self.illegal_operation(other)

        def execute(self, args):
                return RTResult().failure(self.illegal_operation())

        def copy(self):
                raise Exception('No copy method defined')

        def is_true(self):
                return False

        def __bool__(self):
                return self.is_true()

        def illegal_operation(self, other=None):
                # print(self.pos_start, other)
                if not isinstance(other,Value): other = self
                return RTError(
                        self.pos_start, other.pos_end,
                        'Illegal operation',
                        self.context
                )



class Number(Value):
        def __init__(self, value):
                super().__init__()
                self.set('value',value)

        def added_to(self, other):
                if isinstance(other, Number):
                        return type(self)(self.get('value') + other.get('value')).set_context(self.context), None
                else:
                        return None, Value.illegal_operation(self, other)

        def subbed_by(self, other):
                if isinstance(other, Number):
                        return type(self)(self.get('value') - other.get('value')).set_context(self.context), None
                else:
                        return None, Value.illegal_operation(self, other)

        def multed_by(self, other):
                if isinstance(other, Number):
                        return type(self)(self.get('value') * other.get('value')).set_context(self.context), None
                else:
                        return None, Value.illegal_operation(self, other)

        def dived_by(self, other):
                if isinstance(other, Number):
                        if repr(other) == '0':
                                return None, RTError(
                                        other.pos_start, other.pos_end,
                                        'Integer division by zero',
                                        self.context
                                )

                        return type(self)(self.get('value') / other.get('value')).set_context(self.context), None
                else:
                        return None, Value.illegal_operation(self, other)

        def powed_by(self, other):
                if isinstance(other, Number):
                        return type(self)(self.get('value') ** other.get('value')).set_context(self.context), None
                else:
                        return None, Value.illegal_operation(self, other)

        def get_comparison_eq(self, other):
                if isinstance(other, Number):
                        return type(self)(int(self.get('value') == other.get('value'))).set_context(self.context), None
                else:
                        return None, Value.illegal_operation(self, other)

        def get_comparison_ne(self, other):
                if isinstance(other, Number):
                        return type(self)(int(self.get('value') != other.get('value'))).set_context(self.context), None
                else:
                        return None, Value.illegal_operation(self, other)

        def get_comparison_lt(self, other):
                if isinstance(other, Number):
                        return Boolean(int(self.get('value') < other.get('value'))).set_context(self.context), None
                else:
                        return None, Value.illegal_operation(self, other)

        def get_comparison_gt(self, other):
                if isinstance(other, Number):
                        return Boolean(int(self.get('value') > other.get('value'))).set_context(self.context), None
                else:
                        return None, Value.illegal_operation(self, other)

        def get_comparison_lte(self, other):
                if isinstance(other, Number):
                        return Boolean(int(self.get('value') <= other.get('value'))).set_context(self.context), None
                else:
                        return None, Value.illegal_operation(self, other)

        def get_comparison_gte(self, other):
                if isinstance(other, Number):
                        return Boolean(int(self.get('value') >= other.get('value'))).set_context(self.context), None
                else:
                        return None, Value.illegal_operation(self, other)

        def anded_by(self, other):
                if isinstance(other, Number):
                        return Boolean(int(self.get('value') and other.get('value'))).set_context(self.context), None
                else:
                        return None, Value.illegal_operation(self, other)

        def ored_by(self, other):
                if isinstance(other, Number):
                        return Boolean(int(self.get('value') or other.get('value'))).set_context(self.context), None
                else:
                        return None, Value.illegal_operation(self, other)

        def notted(self):
                return Boolean(1 if float(self.get('value')) == 0.0 else 0)

        def copy(self):
                copy = type(self)(self.get('value'))
                copy.set_pos(self.pos_start, self.pos_end)
                copy.set_context(self.context)
                return copy

        def is_true(self):
                return float(self.get('value'))!= 0.0

        def __repr__(self):
                return str(self.get('value'))


class Int(Number):
        def __init__(self,value):
                if isinstance(value,Value): value = value.get('value')
                super().__init__(np.int32(value))
                self.inherit(IntTable)
        @staticmethod
        def desc():
                return "<type int>"
class Long(Number):
        def __init__(self,value):
                if isinstance(value,Value): value = value.get('value')
                super().__init__(np.int64(value))
                self.inherit(LongTable)

        @staticmethod
        def desc():
                return "<type long>"
class Double(Number):
        def __init__(self,value):
                if isinstance(value,Value): value = value.get('value')
                super().__init__(float(value))
                self.inherit(DoubleTable)

        @staticmethod
        def desc():
                return "<type double>"

class Boolean(Number):
        def __init__(self,value):
                super().__init__(1 if value else 0)
                self.inherit(BooleanTable)
        def __bool__(self):
                return self.is_true()
        def __repr__(self):
                return 'true' if self.is_true() else 'false'

class Void(Number):
        def __init__(self,value=None):
                super().__init__(0)
                self.inherit(VoidTable)
        def __bool__(self): return False
        def __repr__(self): return 'null'
       
# print(Boolean(1))
class String(Value):
        def __init__(self,value):
                super().__init__()
                self.set('value',str(value))
                self.inherit(StringTable)
        def idx(self,index):
                try:
                        if isinstance(index,Int):
                                return String(self.get('value')[int(index.get('value'))]), None
                        else:
                                return Value.idx(self,index)
                except:
                        return myNull, None
        def added_to(self,other):
                if isinstance(other,String):
                        return String(self.get('value')+other.get('value')), None
                else:
                        return None, Value.illegal_operation(self, other)

        def multed_by(self,other):
                if isinstance(other,Int):
                        return String(self.get('value')*other.get('value')), None
                else:
                        return None, Value.illegal_operation(self, other)

        def is_true(self):
                return len(self.get('value')) > 0

        def copy(self):
                copy = String(self.get('value'))
                copy.set_pos(self.pos_start, self.pos_end)
                copy.set_context(self.context)
                return copy

        def __repr__(self):
                return self.get('value')
   
class List(Value):
        def __init__(self,elements):
                super().__init__()
                self.set('elements',[elements] if not isinstance(elements,list) else elements)
                self.inherit(ListTable)
        def added_to(self,other):
                if isinstance(other,List):
                        new_list = self.copy()
                        new_list.set('elements',new_list.get('elements')+other.get('elements'))
                        return new_list, None
                else:
                        return None, Value.illegal_operation(self, other)
        
        def multed_by(self,other):
                if isinstance(other,Int):
                        return List(self.get('elements')*(other.get('value'))), None
                else:
                        return None, Value.illegal_operation(self, other)

        def idx(self,other):
                if isinstance(other,Int):
                        try:
                                return self.get('elements')[other.get('value')], None
                        except:
                                return myNull, None
                else:
                        return Value.idx(self,other)
                
        def copy(self):
                copy = List(self.get('elements')[:])
                copy.set_pos(self.pos_start, self.pos_end)
                copy.set_context(self.context)
                return copy
        
        def __repr__(self):
                return '{'+str(self.get('elements'))[1:-1]+'}'

class Function(Value):
        def __init__(self, name, body_node, arg_names, arg_types, return_type, should_auto_return):
                super().__init__()
                self.name = name or "<anonymous>"
                self.body_node = body_node
                self.arg_names = arg_names
                self.arg_types = arg_types
                self.return_type = return_type
                self.should_auto_return = should_auto_return
                self.inherit(FunctionTable)

        def execute(self, args):
                res = RTResult()
                interpreter = Interpreter()
                new_context = Context(self.name, self.context, self.pos_start)
                new_context.symbol_table = SymbolTable(self.context.symbol_table)
                if len(args) > len(self.arg_names):
                        return res.failure(RTError(
                                self.pos_start, self.pos_end,
                                f'{len(args) - len(self.arg_names)} too many args passed into "{self.name}"',
                                self.context
                        ))

                if len(args) < len(self.arg_names):
                        return res.failure(RTError(
                                self.pos_start, self.pos_end,
                                f'{len(self.arg_names) - len(args)} too few args passed into "{self.name}"',
                                self.context
                        ))

                for i in range(len(args)):
                        # if get_type(arg_names)[i] != self.arg_types[i]:
                        #        return res.failure(IncompatibleTypesError(
                        #             args[i].pos_start, args[i].pos_end,
                        #             f'{get_display_type(args[i])} cannot be converted to {display_name(self.arg_types[i])}',
                        #             context
                        #         ))
                        arg_name = self.arg_names[i]
                        arg_value = args[i]
                        arg_value.set_context(new_context)
                        new_context.symbol_table.set(arg_name,arg_value)
                        if get_type(arg_value) != self.arg_types[i]:
                                return res.failure(IncompatibleTypesError(
                                        arg_value.pos_start, arg_value.pos_end,
                                        f'{get_display_type(args[i])} cannot be converted to {display_name(self.arg_types[i])}',
                                        new_context
                                ))
                
                value = res.register(interpreter.visit(self.body_node, new_context))
                if res.should_return(): return res
                ret_value = (value if self.should_auto_return else None) or res.func_return_value or myNull
                return res.success(ret_value)

        def __call__(self,*args):
                        return self.execute(args)

        def copy(self):
                copy = Function(self.name, self.body_node, self.arg_names, self.arg_types, self.return_type, self.should_auto_return)
                copy.set_context(self.context)
                copy.set_pos(self.pos_start, self.pos_end)
                return copy

        def __repr__(self):
                return f"<function {self.name}>"

def createFunction(f):
        def function_wrapper(*args):
                res = RTResult()
                return res.success(f(*args))
        return function_wrapper

def createMethod(f):
        def method_wrapper(this,*args):
                res = RTResult()
                return res.success(f(this,*args))
        # print(method_wrapper.__name__)
        return method_wrapper



IntTable = SymbolTable.fromSymbols({'constructor': Int})
LongTable = SymbolTable.fromSymbols({'constructor': Long})
DoubleTable = SymbolTable.fromSymbols({'constructor': Double})
BooleanTable = SymbolTable.fromSymbols({'constructor': Boolean})
StringTable = SymbolTable.fromSymbols({
        'constructor': String,
        'length': createMethod(lambda this: Int(len(this.get('value'))))
})

ListTable = SymbolTable.fromSymbols({
        'constructor': List,
        'elements': createMethod(lambda this: Int(len(this.get('value'))))
})

FunctionTable = SymbolTable.fromSymbols({'constructor': Function})

# def array(T):
#         class _(Value): pass
#         return _

VoidTable = SymbolTable.fromSymbols({'constructor': Void})
myNull = Void()
# class NativeType(SymbolTable):
#         def set_pos(self, pos_start=None, pos_end=None):
#                 self.pos_start = pos_start
#                 self.pos_end = pos_end
#                 return self
#         def set_context(self, context=None):
#                 self.context = context
#                 return self


# class Int(NativeType): 
#         def __init__(self,value):
#                 super().__init__()
#                 self.set('value', np.int32(int(value)%INT_LIMIT))
#                 self.set_pos()
#                 self.set_context()

#         def __add__(self,that):
#                 if isinstance(that,Double) or isinstance(that,Long):
#                         return that+self
#                 if isinstance(that,Int):
#                         return Int(self.get('value')+that.get('value')).set_context(self.context), None
#         def __sub__(self,that):
#                 if isinstance(that,Double) or isinstance(that,Long):
#                         return -(that-self)
#                 if isinstance(that,Int):
#                         return Int(self.get('value')-that.get('value')).set_context(self.context), None
#         def __mul__(self,that):
#                 if isinstance(that,Double) or isinstance(that,Long):
#                         return that*self
#                 if isinstance(that,Int):
#                         return Int(self.get('value')*that.get('value')).set_context(self.context), None
#         def __truediv__(self,that):
#                 if isinstance(that,Double) or isinstance(that,Long):
#                         return type(that)(self)/(that)
#                 if isinstance(that,Int) and that.get('value') == 0:
#                         return None, RTError(
#                                 that.pos_start, that.pos_end,
#                                 'Integer division by zero',
#                                 self.context
#                         )

#                 return Int(self.get('value')/that.get('value')).set_context(self.context), None
#         def __mod__(self,that):
#                 if isinstance(that,Double) or isinstance(that,Long):
#                         return type(that)(self)%(that)
#                 return Int(self.get('value')%that.get('value')).set_context(self.context), None
#         def __neg__(self):
#                 return Int(-self.get('value')), None
#         def __lt__(self,that): 
#                 return Boolean(self.get('value')<that.get('value')), None
#         def __le__(self,that): 
#                 return Boolean(self.get('value')<=that.get('value')), None
#         def __gt__(self,that): 
#                 return Boolean(self.get('value')>that.get('value')), None
#         def __ge__(self,that): 
#                 return Boolean(self.get('value')>=that.get('value')), None
#         def equalTo(self,that): 
#                 return Boolean(self.get('value')==that.get('value')), None
#         def __repr__(self):
#                 return self.get('value').__repr__()

# class Long(NativeType): 
#         def __init__(self,value):
#                 super().__init__()
#                 self.set('value', np.int64(math.fmod(float(value.__repr__()),LONG_LIMIT)))
#                 self.set_pos()
#                 self.set_context()

#         def __add__(self,that):
#                 if isinstance(that,Double) or isinstance(that,Long):
#                         return type(that)(self)+(that)
#                 return Long(self.get('value')+that.get('value')).set_context(self.context), None
#         def __sub__(self,that):
#                 if isinstance(that,Double) or isinstance(that,Long):
#                         return type(that)(self)-(that)
#                 if isinstance(that,Long):
#                         return Long(self.get('value')-that.get('value')).set_context(self.context), None
#         def __mul__(self,that):
#                 if isinstance(that,Double) or isinstance(that,Long):
#                         return type(that)(self)*(that)
#                 if isinstance(that,Long):
#                         return Long(self.get('value')*that.get('value')).set_context(self.context), None
#         def __truediv__(self,that):
#                 if isinstance(that,Double):
#                         return type(that)(self)/(that)
#                 if  that.get('value') == 0:
#                         return None, RTError(
#                                 that.pos_start, that.pos_end,
#                                 'Integer division by zero',
#                                 self.context
#                         )
#                 if isinstance(that,Long):
#                         return Long(self.get('value')//that.get('value')).set_context(self.context), None
#         def __mod__(self,that):
#                 if isinstance(that,Double) or isinstance(that,Long):
#                         return type(that)(self)%(that)
#                 if isinstance(that,Long):
#                         return Long(self.get('value')%that.get('value')).set_context(self.context), None
#         def __neg__(self):
#                 return Long(-self.get('value')), None
#         def __lt__(self,that): 
#                 return Boolean(self.get('value')<that.get('value')), None
#         def __le__(self,that): 
#                 return Boolean(self.get('value')<=that.get('value')), None
#         def __gt__(self,that): 
#                 return Boolean(self.get('value')>that.get('value')), None
#         def __ge__(self,that): 
#                 return Boolean(self.get('value')>=that.get('value')), None
#         def equalTo(self,that): 
#                 return Boolean(self.get('value')==that.get('value')), None
#         def __repr__(self):
#                 return self.get('value').__repr__()

# class Double(NativeType): 
#         def __init__(self,value):
#                 super().__init__()
#                 self.set('value', float(value.__repr__()))
#                 self.set_pos()
#                 self.set_context()

#         def __add__(self,that):
#                 return Double(self.get('value')+that.get('value')).set_context(self.context), None
#         def __sub__(self,that):
#                 return Double(self.get('value')-that.get('value')).set_context(self.context), None
#         def __mul__(self,that):
#                 return Double(self.get('value')*that.get('value')).set_context(self.context), None
#         def __truediv__(self,that):
#                 if(math.copysign(1,that.get('value')) == -1.0 and that.get('value') == 0.0):
#                         if(self.get('value') == 0.0):
#                                 return Double(math.nan).set_context(self.context), None
#                         return Double(-math.inf).set_context(self.context), None
#                 if(that.get('value') == 0.0):
#                         if(self.get('value') == 0.0):
#                                 return Double(math.nan).set_context(self.context), None
#                         return Double(math.inf), None
#                 return Double(self.get('value')/that.get('value')).set_context(self.context), None
#         def __mod__(self,that):
#                 return Double(self.get('value')%that.get('value')).set_context(self.context), None
#         def __neg__(self):
#                 return Double(-(self.get('value'))), None
#         def __lt__(self,that): 
#                 return Boolean(self.get('value')<that.get('value')), None
#         def __le__(self,that): 
#                 return Boolean(self.get('value')<=that.get('value')), None
#         def __gt__(self,that): 
#                 return Boolean(self.get('value')>that.get('value')), None
#         def __ge__(self,that): 
#                 return Boolean(self.get('value')>=that.get('value')), None
#         def equalTo(self,that): 
#                 return Boolean(self.get('value')==that.get('value')), None
#         def __repr__(self):
#                 if self.get('value') == math.inf:
#                         return "Infinity"
#                 if self.get('value') == -math.inf:
#                         return "-Infinity"
#                 return self.get('value').__repr__()
                
# class Boolean(NativeType): 
#         def __init__(self,value):
#                 super().__init__()
#                 if isinstance(value,SymbolTable) and value.get('value') != None:
#                         value = value.get('value')
#                 self.set('value', not not value)
#                 self.set_pos()
#                 self.set_context()
#         def logicalAnd(self,that):
#                 return Boolean(self.get('value') and that.get('value'))
#         def logicalOr(self,that):
#                 return Boolean(self.get('value') or that.get('value'))
#         def logicalNot(self):
#                 return Boolean(not self.get('value'))
#         def __bool__(self):
#                 return self.get('value')
#         def __repr__(self):
#                 return self.get('value').__repr__().lower()

# class Void(NativeType):
#         def __init__(self):
#                 super().__init__()
#         def __repr__(self): return "None"
#         def __bool__(self): return False

# print(Boolean(1))
# None = Void()
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

        def visit_StringNode(self, node, context):
                res = RTResult()
                return res.success(String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))

        def visit_ListNode(self, node, context):
                res = RTResult()
                elements = []
                for element_node in node.element_nodes:
                        elements.append(res.register(self.visit(element_node, context)))
                        if res.error: return res
                return res.success(List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))


        def visit_NamespaceNode(self, node, context):
                res = RTResult()
                var_name = node.var_name_tok.value
                body_node = node.body_node

                new_context = Context(var_name, context, node.pos_start)
                new_context.symbol_table = SymbolTable(context.symbol_table)
                new_context.symbol_table.set('name',String(var_name))
                body = res.register(self.visit(body_node, new_context))
                # print(new_context.symbol_table.symbols)
                context.symbol_table.set(var_name,new_context.symbol_table)
                return res.success(new_context.symbol_table)

        def visit_KeyNode(self, node, context):
                res = RTResult()
                obj = res.register(self.visit(node.obj_node,context))
                key = res.register(self.visit(node.key_node,context))
                # print(obj.symbols)
                if res.error: return res
                if (not isinstance(obj,Value) or getattr(obj,'idx',None) == None or isinstance(obj,type)) and not getattr(obj,'get',None):
                        return res.success(getattr(obj,repr(key),myNull))
                if type(obj) == SymbolTable:
                        return res.success(myNull if obj.get(repr(key)) == None else obj.get(repr(key)))
                # if getattr(obj,'idx',None) == None or isinstance(obj,type):
                #         return res.failure(RTError(
                #                 node.key_node.pos_start,                            node.key_node.pos_end,
                #                 f'{get_display_type(obj)} is not subscriptable',
                #                 context
                #         ))

                # print(obj,key,obj.idx(key))
                return_value, error = obj.idx(key)
                if error: return res.failure(error)
                return res.success(return_value)
        

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
                
                # if isinstance(value,Value):
                #         value = value.copy().set_pos(node.pos_start, node.pos_end)
                
                # print(context.symbol_table.get(var_name))
                return res.success(value)

        def visit_FuncDefNode(self,node,context):
                res = RTResult()
                func_name = node.var_name_tok.value
                currentValue = context.symbol_table.get(func_name)
                body_node = node.body_node
                arg_names = [arg_name[1].value for arg_name in node.arg_name_toks]
                arg_types = []
                return_type = node.type_tok
                for i in range(0,len(node.arg_name_toks)):
                        arg_types.append(self.visit(VarAccessNode(node.arg_name_toks[i][0]),context).value)

                func_value = Function(func_name, body_node, arg_names, arg_types, return_type,
                                      node.should_auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)

                if currentValue != None and get_type(currentValue) != get_type(func_value):
                        return res.failure(IncompatibleTypesError(
                                node.pos_start, node.pos_end,
                                f'{get_display_type(currentValue)} cannot be converted to {node.type_tok.value}',
                                context
                        ))
                if node.var_name_tok:
                        context.symbol_table.set(func_name, func_value)
                return res.success(func_value)

        def visit_CallNode(self, node, context):
                res = RTResult()
                try:
                        args = []

                        value_to_call = res.register(self.visit(node.node_to_call, context))
                        if res.error: return res
                        if isinstance(value_to_call,Function):
                                return_type = res.register(self.visit(VarAccessNode(value_to_call.return_type),context))
                        else:
                                return_type = None
                        if res.error: return res
                        
                        if isinstance(value_to_call,Function):
                                value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

                        for arg_node in node.arg_nodes:
                                args.append(res.register(self.visit(arg_node, context)))
                                if res.error: return res

                        if type(value_to_call) == SymbolTable:
                                value_to_call = value_to_call.get('constructor')

                        if type(value_to_call) == type:
                                return res.success(value_to_call(*args))
                        elif isFunction(value_to_call):
                                return_value = res.register(value_to_call(*args))
                        elif isinstance(value_to_call,Function):
                                return_value = res.register(value_to_call.execute(args))
                        else:
                                return res.failure(RTError(
                                        node.pos_start, node.pos_end,
                                        f'{get_display_type(value_to_call)} is not callable',
                                        context
                                ))
                        if res.error: return res
                        if return_type and get_type(return_value) != return_type:
                                        return res.failure(IncompatibleTypesError(
                                                node.pos_start, node.pos_end,
                                                f'{get_display_type(return_value)} cannot be converted to {display_name(return_type)}',
                                                context
                                        ))
                        
                                
                        return res.success(return_value)
                except BaseException as ex:
                        raise ex
                        # return res.failure(PythonError(
                        #         node.pos_start, node.pos_end,
                        #         repr(ex),
                        #         context
                        # ))

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
                # print(node.var_name_tok)
                res = RTResult()
                var_name = node.var_name_tok
                if isinstance(var_name,KeyNode):
                        obj_node = var_name.obj_node
                        key_node = var_name.key_node
                        obj =  res.register(self.visit(obj_node,context))
                        key = res.register(self.visit(key_node,context))
                        value = res.register(self.visit(node.value_node,context))

                        if res.error: return res
                        
                        if not isinstance(obj,SymbolTable):
                                setattr(obj,repr(key),value)
                        else:
                                if isinstance(key,String):
                                        obj.set(repr(key),value)
                                        # print(obj)
                                else:
                                        obj.set(key,value)



                                
                        # print(obj.get(key))
                        return res.success(value)
                else:
                        var_name = var_name.value
                        currentValue = context.symbol_table.get(var_name)
                        value = res.register(self.visit(node.value_node,context))
                        if currentValue == None:
                                return res.failure(RTError(
                                        node.pos_start, node.pos_end,
                                        f'"{var_name}" is not defined.',
                                        context
                                ))
                        elif not (get_type(currentValue) == get_type(value)):
                                return res.failure(IncompatibleTypesError(
                                        node.pos_start, node.pos_end,
                                        f'Identifier "{node.var_name_tok.value}" was previously declared with type {get_display_type(currentValue)}, but here has type {get_display_type(value)}.',
                                        context
                                ))

                        if res.error: return res
                        context.symbol_table.set(var_name,value)

                        return res.success(value)
        def visit_BinOpNode(self,node,context):
                res = RTResult()
                result = None
                #print("Found bin op node!")
                left = res.register(self.visit(node.left_node,context))
                right = res.register(self.visit(node.right_node,context))
                if res.error: return res
                if not isinstance(left,SymbolTable):
                        return res.failure(RTError(
                        node.left_node.pos_start, node.right_node.pos_end,
                        'Illegal operation',
                        context
                ))

                if not isinstance(right,SymbolTable):
                        return res.failure(RTError(
                                node.left_node.pos_start, node.right_node.pos_end,
                                'Illegal operation',
                                context
                        ))

                if node.op_tok.type == TT_PLUS:
                        result, error = left.added_to(right)
                elif node.op_tok.type == TT_MINUS:
                        result, error = left.subbed_by(right)
                elif node.op_tok.type == TT_MUL:
                        result, error = left.multed_by(right)
                elif node.op_tok.type == TT_DIV:
                        result, error = left.dived_by(right)
                elif node.op_tok.type == TT_LT:
                        result, error= left.get_comparison_lt(right)
                elif node.op_tok.type == TT_LTE:
                        result, error= left.get_comparison_lte(right)
                elif node.op_tok.type == TT_GT:
                        result, error = left.get_comparison_gt(right)
                elif node.op_tok.type == TT_GTE:
                        result, error= left.get_comparison_gte(right)
                elif node.op_tok.type == TT_EE:
                        result, error = Boolean(str(left) == str(right) and type(left) == type(right)), None
                elif node.op_tok.type == TT_NE:
                        result, error = Boolean(str(left) == str(right) and type(left) == type(right)).notted(), None
                elif node.op_tok.matches(TT_KEYWORD,'and'):
                        result, error = Boolean(left).anded_by(Boolean(right))
                elif node.op_tok.matches(TT_KEYWORD,'or'):
                        result, error = Boolean(left).ored_by(Boolean(right))
                
                if error:
                        return res.failure(error)

                return res.success(result.set_pos(node.pos_start, node.pos_end))

        def visit_UnaryOpNode(self,node,context):
                res = RTResult()
                number = res.register(self.visit(node.node,context))
                error = None
                if res.error: return res
                
                if not isinstance(number,Value):
                        return res.failure(RTError(
                                node.pos_start, node.pos_end,
                                'Illegal operation',
                                context
                        ))

                if node.op_tok.type == TT_MINUS:
                        # print("heh",number.multed_by(Number(-1)))
                        number, error = number.multed_by(Number(-1).set_pos(node.pos_start,node.pos_end).set_context(context))
                elif node.op_tok.matches(TT_KEYWORD,'not'):
                        # if((not getattr(number,"logicalNot",None)) or isinstance(number,type)):
                        #         return res.failure(RTError(
                        #                 node.pos_start, node.pos_end,
                        #                 f'unary operator "not" cannot be applied to an operand of type {get_display_type(number)}',
                        #                 context
                        #         ))
                        number, error = Boolean(number).notted(), None
                # print(number, error)
                if error:
                        return res.failure(error)
                else:
                        return res.success(number)
                
        def visit_IfNode(self, node, context):
                        res = RTResult()
                        for condition, expr in node.cases:
                                condition_value = res.register(self.visit(condition, context))
                                if res.error: return res
                                if Boolean(condition_value):
                                        expr_value = res.register(self.visit(expr, context))
                                        if res.error: return res
                                        return res.success(expr_value)
                         
                        if node.else_case:
                                else_value = res.register(self.visit(node.else_case, context))
                                if res.error: return res 
                                return res.success(else_value)
                         
                        return res.success(myNull)

        def visit_WhileNode(self, node, context):
                res = RTResult()
                temp = myNull
                while True:
                        condition = res.register(self.visit(node.condition_node, context))
                        if res.error: return res

                        if not Boolean(condition): break

                        temp = res.register(self.visit(node.body_node, context))
                        if res.error: return res

                return res.success(temp)


#######################################
# TYPES
#######################################
def get_type(n):
        # print( global_symbol_table.get('ns') ==  global_symbol_table.get('ns'))
        return n._inherit or global_symbol_table.get('ns')

# print(get_type(String("")))
def display_name(theType):
        # print(theType)
        if theType == get_type(Int(0)):
                return "int"
        elif theType == get_type(Long(0)):
                return "long"
        elif theType == get_type(Double(0)):
                return "double"
        elif theType == get_type(Boolean(0)):
                return "boolean"
        elif theType == get_type(Void(0)):
                return "void"
        elif theType == get_type(Function(None,None,None,None,None)):
                return "fn"
        elif theType == get_type(String("")):
                return "string"
        elif theType == get_type(List([])):
                return "list"
        elif theType == get_type(ns(List([]))):
                return "ns"
        else:
                return None

def get_display_type(n):
       return display_name(get_type(n))

# def testy(n):
#         return Int(n)+1

def prettyPrint(n):
       t = str(n)
       if type(n) == SymbolTable:
                if n.get('toString'):
                        return n.get('toString')()
                if repr(n.symbols) == '{}':
                        return '{}'
                result = "{"
                for key in n.symbols:
                       value = n.get(key)
                       result = result+f'{prettyPrint(key)}={prettyPrint(value)}, '
                result = result[0:-2]
                result = f'{result}{"}"}'
                return result
       elif isFunction(n) and not isinstance(n,Function):
        #        print(n.__name__.lower())
               return f'<built-in function {n.__name__.lower()}>'
       else:
               return t
      
      
def skink_len(n):
        res = RTResult()
        if isinstance(n,String):
                return res.success(Int(len(n.get('value'))))
        elif isinstance(n,List):
                return res.success(Int(len(n.get('elements'))))
        else:
                return res.failure(IncompatibleTypesError(
                        n.pos_start, n.pos_end,
                        f'a string or list is required (got type {get_display_type(n)})',
                        n.context
                ))

def skink_substring(n,a,b=None):
        res = RTResult()
        if b == None: b = Int(len(n.get('value')))
        if not isinstance(a,Int):
                return res.failure(RTError(
                        n.pos_start, n.pos_end,
                        f'slice indices must be integers  (got type {get_display_type(n)})',
                        n.context
                ))
        if not isinstance(b,Int):
                return res.failure(RTError(
                        n.pos_start, n.pos_end,
                        f'slice indices must be integers (got type {get_display_type(n)})',
                        n.context
                ))
        return String(n.get('value')[int(a.get('value')):int(b.get('value'))])

def ns(lst): 
        # print(lst)
        # if isinstance(lst,list):
        #         lst = lst[0]
        if not isinstance(lst,List):
                raise Exception()
        t = SymbolTable(global_symbol_table)
        t.set('name','<anonymous>')
        lst = [el.get('elements') for el in lst.get('elements')]
        for u in lst:
                t.set(u[0],u[1])
        # print(t)
        return t


# Int.constructor = createFun(lambda a: Int(a))
# Long.constructor = createFun(lambda a: Long(a))
# Double.constructor = createFun(lambda a: Double(a))
# Boolean.constructor = createFun(lambda a: Boolean(a))
# Void.constructor = createFun(lambda: Void())
# Function.constructor = createFun(lambda: createFun(lambda: run("","void()")))

#########################################
# RUN
#########################################
global_symbol_table = SymbolTable()
global_symbol_table.set('null',myNull)
global_symbol_table.set('pass',myNull)
global_symbol_table.set('true',Boolean(True))
global_symbol_table.set('false',Boolean(False))
global_symbol_table.set('int',get_type(Int(0)))
global_symbol_table.set('long',get_type(Long(0)))
global_symbol_table.set('double',get_type(Double(0)))
global_symbol_table.set('boolean',get_type(Boolean(0)))
global_symbol_table.set('void',get_type(Void(0)))
global_symbol_table.set('string',get_type(String("")))
global_symbol_table.set('fn',get_type(Function(None,None,None,None,None,None)))
global_symbol_table.set('list',get_type(List([])))
global_symbol_table.set('ns',createFunction(ns))

# print(global_symbol_table.symbols)
# global_symbol_table.set('print',print)

# global_symbol_table.set('len',myLen)

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

# print(run)
