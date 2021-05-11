//////////////////////////////////////////////////
//IMPORTS
//////////////////////////////////////////////////
//////////////////////////////////////////////////
//CONSTANTS
//////////////////////////////////////////////////
var DIGITS = "0123456789";

//////////////////////////////////////////////////
//ERRORS
//////////////////////////////////////////////////
class LangError {
    constructor(pos_start, pos_end, error_name, details) {
        this.pos_start = pos_start;
        this.pos_end = pos_end;
        this.error_name = error_name;
        this.details = details;
    }

    toString() {
        var result = this.error_name + ": " + this.details;
        result += '\nFile "' + this.pos_start.fn + '", line ' + (this.pos_start.ln + 1);
        result += "\n\n" + string_with_arrows(this.pos_start.ftxt, this.pos_start, this.pos_end);
        return result;
    }
}

class IllegalCharError extends LangError {
    constructor(pos_start, pos_end, details) {
        super(pos_start, pos_end, "Illegal Character", details);
    }
}

class InvalidSyntaxError extends LangError {
    constructor(pos_start, pos_end, details) {
        super(pos_start, pos_end, "Invalid Syntax", details);
    }
}

class RTError extends LangError {
    constructor(pos_start, pos_end, details) {
        super(pos_start, pos_end, "Runtime Error", details);
    }
}


//////////////////////////////////////////////////
//POSITION
//////////////////////////////////////////////////
class Position {
    constructor(idx, ln, col, fn, ftxt) {
        this.idx = idx;
        this.ln = ln;
        this.col = col;
        this.fn = fn;
        this.ftxt = ftxt;
    }

    advance(current_char) {
        this.idx++;
        this.col++;
        if (this.current_char === "\n") {
            this.ln++;
        }
    }
}

//////////////////////////////////////////////////
//HELPER METHODS
//////////////////////////////////////////////////
Number.prototype.bits = Number.POSITIVE_INFINITY;
Number.prototype.add = function (that) { return this + parseFloat(that); }
Number.prototype.sub = function (that) { return this - parseFloat(that); }
Number.prototype.mul = function (that) { return this * parseFloat(that); }
Number.prototype.div = function (that) { return this / parseFloat(that); }

Int64.prototype.mul = Int64.prototype.multiply;
Int64.prototype.div = Int64.prototype.divide;

function string_with_arrows(text, pos_start, pos_end) {
    //Calculate indices
    var result = text.split("\n")[pos_start.ln];
    var t = Math.max(0, text.indexOf("\n", pos_start.ln));
    result += "\n" + " ".repeat(pos_start.col) + "^".repeat(pos_end.ln - pos_start.ln + 1);
    return result;
}


function copy(obj) {
    //Edge case
    if (obj == null || typeof obj !== "object") { return obj; }
    var result = {};
    var keys_ = Object.getOwnPropertyNames(obj);
    for (var i = 0; i < keys_.length; i++) {
        var key = keys_[i], value = obj[key];
        result[key] = value;
    }

    Object.setPrototypeOf(result, obj.__proto__);
    return result;
}



//////////////////////////////////////////////////
//TOKENS
//////////////////////////////////////////////////
var TT_INT = "INT";
var TT_LONG = "LONG";
var TT_DOUBLE = "DOUBLE";
var TT_PLUS = "PLUS";
var TT_MINUS = "MINUS";
var TT_MUL = "MUL";
var TT_DIV = "DIV";
var TT_LPAREN = "LPAREN";
var TT_RPAREN = "RPAREN";
var TT_EOF = "EOF";

class Token {
    constructor(type_, value = null, pos_start = null, pos_end = null) {
        this.type = type_;
        this.value = value;
        if (pos_start) {
            this.pos_start = copy(pos_start);
            this.pos_end = copy(pos_start);
            this.pos_end.advance();
        }

        if (pos_end) {
            this.pos_end = copy(pos_end);
        }

        // console.log([...arguments],this.pos_start, this.pos_end);
    }


    toString() {
        if (this.value) { return this.type + ":" + this.value; }
        return this.type;
    }
}

//////////////////////////////////////////////////
//INT32
//////////////////////////////////////////////////
var MIN_VALUE = -2147483648;
var MAX_VALUE = 2147483647;

class Int32 {
    constructor(s) {
        s = parseInt(s,10);
        if(s < 0) {
            s += MAX_VALUE;
        }

        var v =  s.toString(2).slice(-32);
        while(v.length < 32) {
            v = "0"+v;
        }

        this.v = v;

    }

    toNumber() { 
        return parseInt(this.value, 10);
    }

    toString() {
        return this.toNumber().toString();
    }
}

//////////////////////////////////////////////////
//LEXER
//////////////////////////////////////////////////
class Lexer {
    constructor(fn, text) {
        this.text = text;
        this.pos = new Position(-1, 0, -1, fn, text);
        this.current_char = null;
        this.advance();
    }

    advance() {
        this.pos.advance(this.current_char);
        this.current_char = (this.pos.idx < this.text.length
            ? this.text.charAt(this.pos.idx)
            : null);
    }

    generate_tokens() {
        var tokens = [];
        while (this.current_char !== null) {
            if (" \t".includes(this.current_char)) {
                this.advance();
            } else if (DIGITS.includes(this.current_char)) {
                tokens.push(this.generate_number());
            } else if (this.current_char === "+") {
                tokens.push(new Token(TT_PLUS, null, this.pos));
                this.advance();
            } else if (this.current_char === "-") {
                tokens.push(new Token(TT_MINUS, null, this.pos));
                this.advance();
            } else if (this.current_char === "*") {
                tokens.push(new Token(TT_MUL, null, this.pos));
                this.advance();
            } else if (this.current_char === "/") {
                tokens.push(new Token(TT_DIV, null, this.pos));
                this.advance();
            } else if (this.current_char === "(") {
                tokens.push(new Token(TT_LPAREN, null, this.pos));
                this.advance();
            } else if (this.current_char === ")") {
                tokens.push(new Token(TT_RPAREN, null, this.pos));
                this.advance();
            } else {
                //return some error
                var pos_start = copy(this.pos);
                var char = this.current_char;
                this.advance();
                return [[], new IllegalCharError(pos_start, this.pos, '"' + char + '"')];
            }
        }

        tokens.push(new Token(TT_EOF, null, this.pos));
        return [tokens, null];
    }

    generate_number() {
        var num_str = "";
        var pos_start = this.pos;
        var dot_count = 0;
        var l_count = 0;

        while (this.current_char !== null && (DIGITS + ".L").includes(this.current_char.toUpperCase())) {
            if (this.current_char === ".") {
                if (dot_count === 1) { break; }
                dot_count++;
                num_str += ".";
            } else if (this.current_char.toUpperCase() === "L") {
                if (l_count === 1) { break; }
                l_count++;
            } else {
                num_str += this.current_char;
            }

            this.advance();
        }

        if (l_count === 1) {
            return new Token(TT_LONG, new Int64(num_str), pos_start, this.pos);
        } else if (dot_count === 1) {
            return new Token(TT_DOUBLE, parseFloat(num_str), pos_start, this.pos);
        } else {
            return new Token(TT_INT, new Int32(num_str), pos_start, this.pos);
        }
    }
}

//////////////////////////////////////////////////
//NODES
//////////////////////////////////////////////////
class NumberNode {
    constructor(tok) {
        this.tok = tok;
        this.pos_start = this.tok.pos_start;
        this.pos_end = this.tok.pos_end;
    }

    toString() {
        return this.tok.toString();
    }
}

class BinOpNode {
    constructor(left_node, op_tok, right_node) {
        this.left_node = left_node;
        this.op_tok = op_tok;
        this.right_node = right_node;

        this.pos_start = this.left_node.pos_start;
        this.pos_end = this.right_node.pos_end;
    }

    toString() {
        return "(" + [this.left_node, this.op_tok, this.right_node].join(",") + ")";
    }
}

class UnaryOpNode {
    constructor(op_tok, node) {
        this.op_tok = op_tok;
        this.node = node;

        this.pos_start = this.op_tok.pos_start;
        this.pos_end = this.op_tok.pos_end;
    }

    toString() {
        return "(" + [this.op_tok, this.node].join(",") + ")";
    }
}


//////////////////////////////////////////////////
//PARSE RESULT
//////////////////////////////////////////////////
class ParseResult {
    constructor() {
        this.error = null;
        this.node = null;
    }

    register(res) {
        if (res instanceof ParseResult) {
            if (res.error) { this.error = res.error; }
            return res.node;
        }

        return res;
    }

    success(node) {
        this.node = node;
        return this;
    }

    failure(error) {
        this.error = error;
        return this;
    }
}



//////////////////////////////////////////////////
//PARSER
//////////////////////////////////////////////////
class Parser {
    constructor(tokens) {
        this.tokens = tokens;
        this.tok_idx = -1;
        this.advance();
    }

    advance() {
        this.tok_idx++;
        if (this.tok_idx < this.tokens.length)
            this.current_tok = this.tokens[this.tok_idx];
        return this.current_tok;
    }

    parse() {
        var res = this.expr();
        if (!res.error && this.current_tok.type !== TT_EOF) {
            return res.failure(new InvalidSyntaxError(
                this.current_tok.pos_start, this.current_tok.pos_end,
                'Expected "+", "-", "*", or "/"'
            ));
        }


        return res;
    }

    atom() {
        var res = new ParseResult();
        var tok = this.current_tok;
        if ([TT_PLUS, TT_MINUS].includes(tok.type)) {
            res.register(this.advance());
            var atom = res.register(this.atom());

            if (res.error) { return res; }
            return res.success(new UnaryOpNode(tok, atom));
        } else if ([TT_INT, TT_LONG, TT_DOUBLE].includes(tok.type)) {
            res.register(this.advance());
            return res.success(new NumberNode(tok));
        } else if (tok.type === TT_LPAREN) {
            res.register(this.advance());
            var expr = res.register(this.expr());
            if (res.error) { return res; }

            if (this.current_tok.type === TT_RPAREN) {
                res.register(this.advance());
                return res.success(expr);
            } else {
                return res.failure(new InvalidSyntaxError(
                    this.current_tok.pos_start, this.current_tok.pos_end,
                    'Expected ")"'
                ))
            }
        } else {
            return res.failure(new InvalidSyntaxError(
                this.current_tok.pos_start, this.current_tok.pos_end,
                "Expected int, long, or double"
            ))
        }
    }

    term() {
        return this.bin_op(() => this.atom(), [TT_MUL, TT_DIV]);
    }

    expr() {
        return this.bin_op(() => this.term(), [TT_PLUS, TT_MINUS]);
    }

    bin_op(func_a, ops, func_b = func_a) {
        var res = new ParseResult();
        var left = res.register(func_a());
        if (res.error) { return res; }
        // console.log(this.current_tok,ops);
        while (ops.includes(this.current_tok.type)) {
            var op_tok = this.current_tok;
            res.register(this.advance());
            var right = res.register(func_b());
            if (res.error) { return res; }
            left = new BinOpNode(left, op_tok, right);
        }

        return res.success(left);

    }

    // bin_op(func_a, ops, func_b=null) {
    //     if(func_b === null) { func_b = func_a; }
    // }
}

//////////////////////////////////////////////////
//VALUES
//////////////////////////////////////////////////
class BaseObject {
    constructor() {
        this.keys = []
        this.values = [];
        this.parent = null;
    }

    set_pos(pos_start=null, pos_end=null) {
        this.pos_start = pos_start;
        this.pos_end = pos_end;
        return this;
    }

    put(key, value) {
        key = key.toString();
        var index = this.keys.indexOf(key);
        if (index == -1) {
            this.keys.push(key);
            this.values.push(value);
        } else {
            this.values[index] = value;
        }
    }

    get(key) {
        key = key.toString();
        var value = this.values[this.keys.indexOf(key)];
        if (value == null && this.parent) {
            return this.parent.get(key);
        } else if (value == null) {
            return value;
        } else {
            return value;
        }
    }


    toString() {
        var keys = this.keys;
        if (keys.length === 0) {
            return "{}";
        } else {
            var result = "{";
            for (var i = 0; i < keys.length; i++) {
                result += keys[i] + ":" + this.get(keys[i]) + ", ";
            }

            result = result.substring(0, result.length - 2);
            result += "}";
            return result;
        }
    }

}



class Namespace extends BaseObject {
    toString() { return "namespace " + super.toString(); }
}

class Num extends BaseObject {
    constructor(value) {
        super();
        this.value = value;
        this.set_pos();
    }


    add(that) {
        if (that instanceof Num) {
            // console.log(this.value.add(that.value));
            return [new Num(this.value.add(that.value)),null];
        }
    }

    sub(that) {
        if (that instanceof Num) {
            return [new Num(this.value.sub(that.value)),null];
        }
    }

    mul(that) {
        if (that instanceof Num) {
            return [new Num(this.value.mul(that.value)),null];
        }
    }

    div(that) {
        if (that instanceof Num) {
            return [new Num(this.value.div(that.value)),null];
        }
    }

    neg() { return new Num(this.value.mul(-1)); }

    toString() { return this.value.toString(); }
}


class Integer extends Num { constructor(value) { super(new Int32(value)); } }
class Long extends Num { constructor(value) { super(new Int64(value)); } }
class Double extends Num { constructor(value) { super(parseFloat(value)); } }


class RTResult {
    constructor() {
        this.error = null;
        this.value = null;
    }

    register(res) {
        if (res instanceof RTResult) {
            if (res.error) { this.error = res.error; }
            return res.value;
        }

        return res;
    }

    success(node) {
        this.value = node;
        return this;
    }

    failure(error) {
        this.error = error;
        return this;
    }
}


//////////////////////////////////////////////////
//INTERPRETER
//////////////////////////////////////////////////
class Interpreter {
    visit(node) {
        var method_name = "visit_" + node.constructor.name;
        //"visit_BinOpNode"
        var method = () => (this[method_name] || this.no_visit_method).call(this, node);
        return method();
    }

    no_visit_method(node) {
        var method_name = "visit_" + node.constructor.name;
        throw new Error("no " + method_name + " method defined");
    }

    //////////////////////////////////////////////////
    visit_NumberNode(node) {
        var res = new RTResult();
        if (node.tok.type === TT_INT) {
            return res.success(new Integer(node.tok.value).set_pos(this.pos_start, this.pos_end));
        } else if (node.tok.type === TT_LONG) {
            return res.success(new Long(node.tok.value).set_pos(this.pos_start, this.pos_end));
        } else {
        return res.success(new Double(node.tok.value).set_pos(this.pos_start, this.pos_end));
        }
    }


    visit_BinOpNode(node) {
        var res = new RTResult();
        var left =  res.register(this.visit(node.left_node));
        var right = res.register(this.visit(node.right_node));
        var result, error;
        if (node.op_tok.type === TT_PLUS) {
            [result, error] = left.add(right);
        } else if (node.op_tok.type === TT_MINUS) {
            [result, error] = left.sub(right);
        } else if (node.op_tok.type === TT_MUL) {
            [result, error] = left.mul(right);
        } else if (node.op_tok.type === TT_DIV) {
            [result, error] = left.div(right);
        }

        return res.success(result.set_pos(node.pos_start,node.pos_end));
    }

    visit_UnaryOpNode(node) {
        // console.log("Found unary op node!");
        var res = new RTResult();
        var number = res.register(this.visit(node.node));
        if (node.op_tok.type === TT_MINUS) {
            number = number.neg();
        }

        return res.success(number);
    }
}

//////////////////////////////////////////////////
//RUN
//////////////////////////////////////////////////
function run(text, fn = "<anonymous>") {
    //Generate tokens
    var lexer = new Lexer(fn, text);
    var [tokens, error] = lexer.generate_tokens();
    if (error) { return [null, error]; }
    //Generate AST
    var parser = new Parser(tokens);
    var ast = parser.parse();
    if (ast.error) { return [null, ast.error]; }

    //Run program
    var interpreter = new Interpreter();
    var result = interpreter.visit(ast.node)
    // console.log(result);
    return [result.value, result.error];
}

function run_file(url) {
    if (typeof require !== "function"
        || typeof Buffer !== "function"
        || typeof Buffer.from !== "function") {
        throw new Error("run_file() uses the Node.js.");
    } else {
        var fs = require("fs");
        var path = require("path");

        var t = url.split(/\/|\\/g);
        var text = fs.readFileSync(path.join(__dirname, url), "utf-8");
        var u = run(text, t[t.length - 1]);
        var [result, error] = u;
        if (error) {
            console.log(error.toString());
        } else {
            console.log(result.toString());
        }
    }
}

//Module exports.
module.exports = { run, run_file };