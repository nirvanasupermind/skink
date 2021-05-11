//Skink source code
//Usage permitted under terms of MIT License
"use strict";

var util = require("util");
var nightjar = require("nightjar");

///////////////////////////////////////
//CONSTANTS
///////////////////////////////////////
var DIGITS = "0123456789";


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
    var result = this.pos_start.fn+":"+(this.pos_start.ln+1)+":"+(this.pos_start.col+1)+": "+ this.error_name + ": " + this.details;
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


///////////////////////////////////////
//UTILITY FUNCTIONS
///////////////////////////////////////
function or(items) {
    var t = items.map(quote);
    return t.slice(0, -1).join(", ") + " or " + t[t.length - 1]
}

function or1(items) {
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
    "PLUS",
    "MINUS",
    "MUL",
    "DIV",
    "LPAREN",
    "RPAREN",
    "EOF"
]);



function Token(type_, value = null, pos_start = null, pos_end = null) {
    if (pos_end === null) pos_end = pos_start !== null ? pos_start + 1 : null;

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
        } else if (DIGITS.includes(this.current_char)) {
            tokens.push(this.generate_number());
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
        return new Token(TokenType.DOUBLE, parseFloat(num_str), pos_start, this.pos);
    } else if (l_count === 1) {
        return new Token(TokenType.LONG, nightjar.Int64(num_str), pos_start, this.pos);
    } else {
        return new Token(TokenType.INT, nightjar.Int32(num_str), pos_start, this.pos);
    }
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
    // console.log(left_node, op_tok, right_node)
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
    return "(" + this.op_tok + ", "+this.node+")";
}

///////////////////////////////////////
//PARSE RESULT
///////////////////////////////////////
function ParseResult() {
    this.error = null;
    this.node = null;
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
    var res = this.expr();


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
    if(tok.type === TokenType.MINUS) {
        res.register(this.advance());
        var atom = res.register(this.atom());

        return res.success(new UnaryOpNode(tok, atom));
    } else if(tok.type === TokenType.LPAREN) {
        res.register(this.advance());
        var expr = res.register(this.expr());

        if(this.current_tok.type !== TokenType.RPAREN) {
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
            "Unexpected end of input"
        ))
    }
}

Parser.prototype.term = function () {
    return this.bin_op(this.atom, [TokenType.MUL, TokenType.DIV]);
}

Parser.prototype.expr = function () {
    if(this.current_tok.type === TokenType.EOF) {
        var res = new ParseResult();
    return res.success(null);
    }


    return this.bin_op(this.term, [TokenType.PLUS, TokenType.MINUS]);
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
//RUN
///////////////////////////////////////
function run(fn, text) {
    //Generate tokens
    var lexer = new Lexer(fn, text);
    var [tokens, error] = lexer.generate_tokens();
    if (error) return [null, error];

    //Generate AST
    var parser = new Parser(tokens);
    var res = parser.parse();

    return [res.node, res.error];
}

function skink(file) { return; }
skink.run = run;

module.exports = skink;
