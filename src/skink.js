//Skink source code
//Usage permitted under terms of MIT License
"use strict";

var util = require("util");
var fs = require("fs");
var nightjar = require("nightjar");

///////////////////////////////////////
//CONSTANTS
///////////////////////////////////////
var DEFAULT_MAX_LENGTH = 80;
var DIGITS = "0123456789";
var VOWELS = "aeiou";
var LETTERS = "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
var LETTERS_DIGITS = LETTERS + DIGITS;

///////////////////////////////////////
//ERRORS
///////////////////////////////////////
function BaseError(pos_start, pos_end, error_name, details) {
    this.pos_start = pos_start;
    this.pos_end = pos_end;
    this.error_name = error_name;
    this.details = details;
}

BaseError.prototype.toString = function () {
    var result = this.pos_start.fn + ":" + (this.pos_start.ln + 1) + ":" + (this.pos_start.col + 1) + ": " + this.error_name + ": " + this.details;
    return result;
}

function IllegalCharError(pos_start, pos_end, details) {
    // console.log(pos_start, pos_end)
    BaseError.call(this, pos_start, pos_end, "Illegal Character", details);
}

util.inherits(IllegalCharError, BaseError);

function InvalidSyntaxError(pos_start, pos_end, details) {
    // console.log(pos_start, pos_end)
    BaseError.call(this, pos_start, pos_end, "Invalid Syntax", details);
}

util.inherits(InvalidSyntaxError, BaseError);

function RTError(pos_start, pos_end, details, context) {
    // console.log(pos_start, pos_end)
    BaseError.call(this, pos_start, pos_end, "Runtime Error", details);
    this.context = context;
}

util.inherits(RTError, BaseError);
RTError.prototype.toString = function () {
    var result = this.pos_start.fn + ":" + (this.pos_start.ln + 1) + ":" + (this.pos_start.col + 1) + ": " + this.error_name + ": " + this.details;
    result += "\n" + this.generate_traceback();
    return result;
}

RTError.prototype.generate_traceback = function () {
    var result = "";
    var pos = this.pos_start;
    var ctx = this.context;

    while (ctx) {
        result += "\t" + pos.fn + ":" + (pos.ln + 1) + ":" + (pos.col + 1) + ": in " + ctx.display_name
        pos = ctx.parent_entry_pos;;
        ctx = ctx.parent;
    }


    return "Stack traceback:\n" + result;
}


///////////////////////////////////////
//UTILITY FUNCTIONS
///////////////////////////////////////
function isNumber(a) { return typeof a === "number"; }
function toNumber(a) { return isNumber(a) ? a : parseFloat(a); }

function cons(a, b) {
    var t = add(a.value, b.value).constructor;

    if (t === nightjar.Int32) return Integer;
    if (t === nightjar.Int64) return Long;

    return Double;
}
function add(a, b) {
    if (isNumber(a) || isNumber(b)) {
        return toNumber(a) + toNumber(b);
    } else if (b instanceof nightjar.Int64) {
        return b.add(a);
    } else {
        return a.add(b);
    }
}

function sub(a, b) {
    if (isNumber(a) || isNumber(b)) {
        return toNumber(a) - toNumber(b);
    } else if (b instanceof nightjar.Int64) {
        return b.sub(a).neg();
    } else {
        return a.sub(b);
    }
}

function mul(a, b) {
    if (isNumber(a) || isNumber(b)) {
        return toNumber(a) * toNumber(b);
    } else if (b instanceof nightjar.Int64) {
        return b.mul(a);
    } else {
        return a.mul(b);
    }
}

function div(a, b) {
    if (isNumber(a) || isNumber(b)) {
        return toNumber(a) / toNumber(b);
    } else if (b instanceof nightjar.Int64) {
        return nightjar.Int64(a).div(b);
    } else {
        return a.div(b);
    }
}


function neg(a) {
    if (isNumber(a)) {
        return -a;
    } else {
        return a.neg();
    }
}



//taken from https://stackoverflow.com/questions/13861254/json-stringify-deep-objects
// This is based on Douglas Crockford's code ( https://github.com/douglascrockford/JSON-js/blob/master/json2.js )
(function () {
    'use strict';

    var DEFAULT_MAX_DEPTH = 6;
    var DEFAULT_ARRAY_MAX_LENGTH = 50;
    var seen; // Same variable used for all stringifications

    Date.prototype.toPrunedJSON = Date.prototype.toJSON;
    String.prototype.toPrunedJSON = String.prototype.toJSON;

    var cx = /[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,
        escapable = /[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,
        meta = {    // table of character substitutions
            '\b': '\\b',
            '\t': '\\t',
            '\n': '\\n',
            '\f': '\\f',
            '\r': '\\r',
            '"': '\\"',
            '\\': '\\\\'
        };

    function quote(string) {
        escapable.lastIndex = 0;
        return escapable.test(string) ? '"' + string.replace(escapable, function (a) {
            var c = meta[a];
            return typeof c === 'string'
                ? c
                : '\\u' + ('0000' + a.charCodeAt(0).toString(16)).slice(-4);
        }) + '"' : '"' + string + '"';
    }

    function str(key, holder, depthDecr, arrayMaxLength) {
        var i,          // The loop counter.
            k,          // The member key.
            v,          // The member value.
            length,
            partial,
            value = holder[key];
        if (value && typeof value === 'object' && typeof value.toPrunedJSON === 'function') {
            value = value.toPrunedJSON(key);
        }

        switch (typeof value) {
            case 'string':
                return quote(value);
            case 'number':
                return isFinite(value) ? String(value) : 'null';
            case 'boolean':
            case 'null':
                return String(value);
            case 'object':
                if (!value) {
                    return 'null';
                }
                if (depthDecr <= 0 || seen.indexOf(value) !== -1) {
                    return '"-pruned-"';
                }
                seen.push(value);
                partial = [];
                if (Object.prototype.toString.apply(value) === '[object Array]') {
                    length = Math.min(value.length, arrayMaxLength);
                    for (i = 0; i < length; i += 1) {
                        partial[i] = str(i, value, depthDecr - 1, arrayMaxLength) || 'null';
                    }
                    v = partial.length === 0
                        ? '[]'
                        : '[' + partial.join(',') + ']';
                    return v;
                }
                for (k in value) {
                    if (Object.prototype.hasOwnProperty.call(value, k)) {
                        try {
                            v = str(k, value, depthDecr - 1, arrayMaxLength);
                            if (v) partial.push(quote(k) + ':' + v);
                        } catch (e) {
                            // this try/catch due to some "Accessing selectionEnd on an input element that cannot have a selection." on Chrome
                        }
                    }
                }
                v = partial.length === 0
                    ? '{}'
                    : '{' + partial.join(',') + '}';
                return v;
        }
    }

    JSON.pruned = function (value, depthDecr, arrayMaxLength) {
        seen = [];
        depthDecr = depthDecr || DEFAULT_MAX_DEPTH;
        arrayMaxLength = arrayMaxLength || DEFAULT_ARRAY_MAX_LENGTH;
        return str('', { '': value }, depthDecr, arrayMaxLength);
    };

}());


function or(items) {
    return items.slice(0, -1).join(", ") + " or " + items[items.length - 1];
}


//taken from https://stackoverflow.com/questions/122102/what-is-the-most-efficient-way-to-deep-clone-an-object-in-javascript
function clone(obj) {
    if (obj === null || typeof (obj) !== 'object' || 'isActiveClone' in obj)
        return obj;

    var temp = new obj.constructor();

    for (var key in obj) {
        if (Object.prototype.hasOwnProperty.call(obj, key)) {
            obj['isActiveClone'] = null;
            temp[key] = clone(obj[key]);
            delete obj['isActiveClone'];
        }
    }
    return temp;
}




//taken from https://stackoverflow.com/questions/287903/what-is-the-preferred-syntax-for-defining-enums-in-javascript
var buildSet = function (array) {
    var set = {};
    for (var i in array) {
        var item = array[i];
        set[item] = item;
    }
    return set;
}


function quote(str) { return '"' + str + '"'; }

///////////////////////////////////////
//POSITION
///////////////////////////////////////
function Position(idx, ln, col, fn, ftxt) {
    this.idx = idx;
    this.ln = ln;
    this.col = col;
    this.fn = fn;
    this.ftxt = ftxt;
}

Position.prototype.advance = function (current_char = null) {
    this.idx++;
    this.col++;
    if (current_char === "\n") {
        this.ln++;
        this.col = 0;
    }

    return this;
}


///////////////////////////////////////
//TOKENS
///////////////////////////////////////
var TokenType = buildSet([
    "INT",
    "LONG",
    "DOUBLE",
    "IDENTIFIER",
    "KEYWORD",
    "PLUS",
    "MINUS",
    "MUL",
    "DIV",
    "EQ",
    "LPAREN",
    "RPAREN",
    "NEWLINE",
    "EOF"
]);

var KEYWORDS = [];


function Token(type_, value = null, pos_start = null, pos_end = null) {
    if (pos_end === null) pos_end = pos_start !== null ? clone(pos_start).advance() : null;

    this.type = type_;
    this.value = value;
    this.pos_start = pos_start;
    this.pos_end = pos_end;
}

Token.prototype.toString = function () {
    if (this.value) return this.type + ":" + this.value;
    return this.type;
}


///////////////////////////////////////
//LEXER
///////////////////////////////////////
function Lexer(fn, text) {
    this.fn = fn;
    this.text = text;
    this.pos = new Position(-1, 0, -1, fn, text);
    this.current_char = null;
    this.advance();
}

Lexer.prototype.advance = function () {
    this.pos.advance(this.current_char);
    this.current_char = this.pos.idx < this.text.length
        ? this.text.charAt(this.pos.idx)
        : null;
}

Lexer.prototype.generate_tokens = function () {
    var tokens = [];
    while (this.current_char !== null) {
        if (" \t".includes(this.current_char)) {
            this.advance();
        } else if (";\n\r".includes(this.current_char)) {
            tokens.push(new Token(TokenType.NEWLINE, null, this.pos));
            this.advance();
        } else if (DIGITS.includes(this.current_char)) {
            tokens.push(this.generate_number());
        } else if (LETTERS.includes(this.current_char)) {
            tokens.push(this.generate_identifier());
        } else if (this.current_char === "+") {
            tokens.push(new Token(TokenType.PLUS, null, this.pos));
            this.advance();
        } else if (this.current_char === "-") {
            tokens.push(new Token(TokenType.MINUS, null, this.pos));
            this.advance();
        } else if (this.current_char === "*") {
            tokens.push(new Token(TokenType.MUL, null, this.pos));
            this.advance();
        } else if (this.current_char === "/") {
            tokens.push(new Token(TokenType.DIV, null, this.pos));
            this.advance();
        } else if (this.current_char === "=") {
            tokens.push(new Token(TokenType.EQ, null, this.pos));
            this.advance();
        } else if (this.current_char === "(") {
            tokens.push(new Token(TokenType.LPAREN, null, this.pos));
            this.advance();
        } else if (this.current_char === ")") {
            tokens.push(new Token(TokenType.RPAREN, null, this.pos));
            this.advance();
        } else {
            //return some error

            var char = this.current_char;
            var pos_start = clone(this.pos);

            this.advance();
            return [[], new IllegalCharError(
                pos_start, this.pos,
                quote(char)
            )];
        }
    }

    tokens.push(new Token(TokenType.EOF, null, this.pos));
    return [tokens, null];
}

Lexer.prototype.generate_number = function () {
    var pos_start = clone(this.pos);
    var num_str = "";
    var dot_count = 0;
    var l_count = 0;
    while (this.current_char !== null && (DIGITS + ".").includes(this.current_char)) {
        if (this.current_char === ".") {
            if (dot_count === 1) break;
            dot_count++;
            num_str += ".";
        } else {
            num_str += this.current_char;
        }

        this.advance();
    }

    if (this.current_char && this.current_char.toUpperCase() === "L") {
        l_count++;
        this.advance();
    }


    if (dot_count === 1) {
        return new Token(TokenType.DOUBLE, toNumber(num_str), pos_start, this.pos);
    } else if (l_count === 1) {
        return new Token(TokenType.LONG, nightjar.Int64(num_str), pos_start, this.pos);
    } else {
        return new Token(TokenType.INT, nightjar.Int32(num_str), pos_start, this.pos);
    }
}

Lexer.prototype.generate_identifier = function () {
    var id_str = "";
    var pos_start = clone(this.pos);
    while (this.current_char !== null && LETTERS_DIGITS.includes(this.current_char)) {
        id_str += this.current_char;
        this.advance();
    }

    var tok_type = KEYWORDS.includes(id_str) ? TokenType.KEYWORD : TokenType.IDENTIFIER;
    return new Token(tok_type, id_str, pos_start, this.pos);
}
///////////////////////////////////////
//NODES
///////////////////////////////////////
function NumberNode(tok) {
    this.tok = tok;
    this.pos_start = this.tok.pos_start;
    this.pos_end = this.tok.pos_end;
}

NumberNode.prototype.toString = function () { return this.tok.toString(); }

function BinOpNode(left_node, op_tok, right_node) {
    this.left_node = left_node;
    this.op_tok = op_tok;
    this.right_node = right_node;

    this.pos_start = this.left_node.pos_start;
    this.pos_end = this.right_node.pos_end;
}

BinOpNode.prototype.toString = function () {
    return "(" + [this.left_node, this.op_tok, this.right_node].join(", ") + ")";
}

function UnaryOpNode(op_tok, node) {
    this.op_tok = op_tok;
    this.node = node;

    this.pos_start = this.op_tok.pos_start;
    this.pos_end = this.node.pos_end;
}

UnaryOpNode.prototype.toString = function () {
    return "(" + this.op_tok + ", " + this.node + ")";
}

function MultilineNode(lines, pos_start, pos_end) {
    this.lines = lines;
    this.pos_start = pos_start;
    this.pos_end = pos_end;
}

function EmptyNode(pos_start) {
    this.pos_start = pos_start;
    this.pos_end = pos_start;
}

///////////////////////////////////////
//PARSE RESULT
///////////////////////////////////////
function ParseResult() {
    this.error = null;
    this.value = null;
}

ParseResult.prototype.register = function (res) {
    if (res instanceof ParseResult) {
        if (res.error) this.error = res.error;
        return res.node;
    }

    return res;
}

ParseResult.prototype.success = function (node) {
    this.node = node;
    return this;
}

ParseResult.prototype.failure = function (error) {
    this.error = error;
    return this;
}

///////////////////////////////////////
//PARSER
///////////////////////////////////////
function Parser(tokens) {
    this.tokens = tokens;
    this.tok_idx = -1;
    this.advance();
}

Parser.prototype.advance = function () {
    this.tok_idx++;
    if (this.tok_idx < this.tokens.length) {
        this.current_tok = this.tokens[this.tok_idx];
    }

    return this.current_tok;
}

Parser.prototype.parse = function () {
    var res = this.file();


    if (!res.error && this.current_tok.type !== TokenType.EOF) {
        return res.failure(new InvalidSyntaxError(
            this.current_tok.pos_start, this.current_tok.pos_end,
            "Expected end of input"
        ))
    }

    return res;
}

Parser.prototype.atom = function () {
    var res = new ParseResult();


    var tok = this.current_tok;
    if ([TokenType.PLUS, TokenType.MINUS].includes(tok.type)) {
        res.register(this.advance());
        var atom = res.register(this.atom());
        if (res.error) return res;

        return res.success(new UnaryOpNode(tok, atom));
    } else if (tok.type === TokenType.LPAREN) {
        res.register(this.advance());
        var expr = res.register(this.expr());

        if (this.current_tok.type !== TokenType.RPAREN) {
            return res.failure(new InvalidSyntaxError(
                this.current_tok.pos_start, this.current_tok.pos_end,
                'Expected ")"'
            ));
        }

        res.register(this.advance());
        return res.success(expr);
    } else if ([TokenType.INT, TokenType.LONG, TokenType.DOUBLE].includes(tok.type)) {
        res.register(this.advance());
        return res.success(new NumberNode(tok));
    } else {
        return res.failure(new InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected " + or(["int", "long", "double", "identifier", '"+"', '"-"', '"("'])
        ))
    }
}

Parser.prototype.term = function () {
    return this.bin_op(this.atom, [TokenType.MUL, TokenType.DIV]);
}

Parser.prototype.expr = function () {
    if (this.current_tok.type === TokenType.EOF || this.current_tok.type === TokenType.NEWLINE) {
        var res = new ParseResult();
        return res.success(new EmptyNode(this.pos_start));
    }

    return this.bin_op(this.term, [TokenType.PLUS, TokenType.MINUS]);
}

Parser.prototype.file = function () {
    var res = new ParseResult();
    var pos_start = this.current_tok.pos_start;
    var first_line = res.register(this.expr());
    if (res.error) return res;

    var lines = [first_line];
    while (this.current_tok.type === TokenType.NEWLINE) {
        res.register(this.advance());
        var pos = this.current_tok.pos_start;
        if (this.current_tok.type === TokenType.NEWLINE) {
            lines.push(new EmptyNode(pos));
        } else {

            var line = res.register(this.expr());
            if (res.error) return res;

            lines.push(line);
        }
    }

    return res.success(new MultilineNode(lines, pos_start, this.current_tok.pos_end))
}


Parser.prototype.bin_op = function (func, ops) {
    var res = new ParseResult();
    var left = res.register(func.call(this));
    if (res.error) return res;

    while (ops.includes(this.current_tok.type)) {
        var op_tok = this.current_tok;
        res.register(this.advance());

        var right = res.register(func.call(this));
        if (res.error) return res;

        left = new BinOpNode(left, op_tok, right);
    }

    return res.success(left);
}

///////////////////////////////////////
//VALUES
///////////////////////////////////////
function BaseObject(parent = object_meta) {
    // console.log(this)
    this.keys = [];
    this.values = [];
    this.parent = parent;
    this.set_pos();
    this.set_context();
}

BaseObject.prototype.set_context = function (context = null) {
    this.context = context;
    return this;
}

BaseObject.prototype.set_pos = function (pos_start = null, pos_end = null) {
    this.pos_start = pos_start;
    this.pos_end = pos_end;

    return this;
}
BaseObject.prototype.set = function (key, value) {
    var index = this.keys.indexOf(JSON.pruned(key));
    if (index === -1) {
        this.keys.push(JSON.pruned(key));
        this.values.push(value);
    } else {
        this.values[index] = value;
    }
}

BaseObject.prototype.get = function (key) {
    var index = this.keys.indexOf(JSON.pruned(key));
    if (index === -1 && this.parent) return this.parent.get(key);
    return this.keys[index];
}


BaseObject.prototype.exists = function (key) {
    var index = this.keys.indexOf(JSON.pruned(key));
    return index > -1;
}

BaseObject.prototype.toString = function () {
    if (this.keys.length >= DEFAULT_MAX_LENGTH) {
        return [
            "{",
            this.keys.slice(0, DEFAULT_MAX_LENGTH).map((el, i) => JSON.parse(el) + "=" + JSON.parse(values[i])).join(", "),
            "...}"
        ].join("");
    } else {
        return "{" + this.keys.map((el, i) => JSON.parse(el) + "=" + JSON.parse(values[i])).join(", ") + "}";
    }
}

var object_meta = new BaseObject(null);
var namespace_meta = new BaseObject(object_meta);
var num_meta = new BaseObject(object_meta);
var int_meta = new BaseObject(num_meta);
var long_meta = new BaseObject(num_meta);
var double_meta = new BaseObject(num_meta);

function Namespace(parent = namespace_meta) {
    BaseObject.call(this, parent);
}

util.inherits(Namespace, BaseObject);

function Num(value) {
    BaseObject.call(this, num_meta);
    this.value = value;
}

util.inherits(Num, BaseObject);


Num.prototype.add = function (other) {
    if (other instanceof Num) {
        return [new (cons(this, other))(add(this.value, other.value)), null];
    }
}

Num.prototype.sub = function (other) {
    if (other instanceof Num) {
        return [new (cons(this, other))(sub(this.value, other.value)), null];
    }
}

Num.prototype.mul = function (other) {
    if (other instanceof Num) {
        return [new (cons(this, other))(mul(this.value, other.value)), null];
    }
}

Num.prototype.div = function (other) {
    if (other instanceof Num) {
        if (other.value.toString() === "0" && !isNumber(other.value)) {
            return [null, new RTError(
                other.pos_start,
                other.pos_end,
                "attempt to divide by zero",
                this.context
            )];
        }

        return [new (cons(this, other))(div(this.value, other.value)), null];
    }
}

Num.prototype.neg = function () {
    return [new (this.constructor)(neg(this.value)), null];
}

Num.prototype.toString = function () { return this.value.toString(); }



function Integer(value) {
    Num.call(this, nightjar.Int32(value));
    this.parent = int_meta;
}

util.inherits(Integer, Num);

function Long(value) {
    Num.call(this, nightjar.Int64(value));
    this.parent = long_meta;
}

util.inherits(Long, Num);

function Double(value) {
    Num.call(this, toNumber(value));
    this.parent = double_meta;
}

util.inherits(Double, Num);


///////////////////////////////////////
//RUNTIME RESULT
///////////////////////////////////////
function RTResult() {
    this.error = null;
    this.value = null;
}

RTResult.prototype.register = function (res) {
    // console.log("!!!!")
    if (res instanceof RTResult) {
        if (res.error) this.error = res.error;
        return res.value;
    }

    return res;
}

RTResult.prototype.success = function (value) {
    this.value = value;
    return this;
}

RTResult.prototype.failure = function (error) {
    this.error = error;
    return this;
}

///////////////////////////////////////
//CONTEXT
///////////////////////////////////////
function Context(display_name, parent = null, parent_entry_pos = null) {
    this.display_name = display_name;
    this.parent = parent;
    this.parent_entry_pos = parent_entry_pos;
}

///////////////////////////////////////
//INTERPRETER
///////////////////////////////////////
function Interpreter() { }
Interpreter.prototype.visit = function (context, node) {
    //visit_BinOpNode
    var method_name = "visit_" + node.constructor.name;
    var method = this[method_name] || this.no_visit_method;
    return method.call(this, context, node);
}

Interpreter.prototype.no_visit_method = function (context, node) {
    var method_name = "visit_" + node.constructor.name;
    throw new Error("no visit method defined " + method_name);
}

Interpreter.prototype.visit_EmptyNode = function (node) {
    return new RTResult().success(null);
}

Interpreter.prototype.visit_MultilineNode = function (context, node) {
    var res = new RTResult();
    var tmp = [];
    for (var i = 0; i < node.lines.length; i++) {
        if (i >= 1 && node.lines[i] instanceof EmptyNode) continue;
        var result = res.register(this.visit(context, node.lines[i]));
        if (res.error) return res;
        tmp.push(result);
    }


    return res.success(tmp.pop());
}

Interpreter.prototype.visit_NumberNode = function (context, node) {
    var res = new RTResult();
    if (node.tok.type === TokenType.INT) {
        return res.success(
            new Integer(node.tok.value)
                .set_pos(node.tok.pos_start, node.tok.pos_end)
                .set_context(context)
        );
    } else if (node.tok.type === TokenType.LONG) {
        return res.success(
            new Long(node.tok.value)
                .set_pos(node.tok.pos_start, node.tok.pos_end)
                .set_context(context)
        );
    } else {
        return res.success(
            new Double(node.tok.value)
                .set_pos(node.tok.pos_start, node.tok.pos_end)
                .set_context(context)
        );
    }
}

Interpreter.prototype.visit_BinOpNode = function (context, node) {
    var res = new RTResult();

    var left = res.register(this.visit(context, node.left_node));
    var right = res.register(this.visit(context, node.right_node));

    if (res.error) return res;

    // console.log(left.toString(),right.toString())
    var result, error;
    if (node.op_tok.type === TokenType.PLUS) {
        [result, error] = left.add(right);
    } else if (node.op_tok.type === TokenType.MINUS) {
        [result, error] = left.sub(right);
    } else if (node.op_tok.type === TokenType.MUL) {
        [result, error] = left.mul(right);
    } else {
        [result, error] = left.div(right);
    }

    if (error) return res.failure(error);
    return res.success(result.set_pos(node.pos_start, node.pos_end).set_context(context));
}

Interpreter.prototype.visit_UnaryOpNode = function (context, node) {
    var res = new RTResult();

    var number = res.register(this.visit(context, node.node));
    if (res.error) return res;

    var error;

    if (node.op_tok.type === TokenType.MINUS) {
        [number, error] = number.neg();
    }

    if (error) return res.failure(error);
    return res.success(number.set_pos(node.pos_start, node.pos_end).set_context(context));
}



///////////////////////////////////////
//RUN
///////////////////////////////////////
function run(fn, text) {
    //Generate tokens
    var lexer = new Lexer(fn, text);
    var [tokens, error] = lexer.generate_tokens();
    if (error) return [null, error];

    //Generate AST
    var parser = new Parser(tokens);
    var ast = parser.parse();
    if (ast.error) return [null, ast.error];

    //Run program
    var interpreter = new Interpreter();
    var context = new Context("<program>");

    var result = interpreter.visit(context, ast.node);

    return [result.value, result.error];

}



function skink(file) {
    return run(require("path").resolve(file).split("/").pop(), fs.readFileSync(file, "utf-8"));
}

skink.eval = function (str) {
    return run("<anonymous>", str);
}

skink.run = run;

module.exports = skink;
