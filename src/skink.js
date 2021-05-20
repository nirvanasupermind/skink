//Skink source code
//Usage permitted under terms of MIT License
"use strict";

var util = require("util");
var fs = require("fs");
var i32 = require("i32");
var { Int64 } = require("int64_t");

///////////////////////////////////////
//CONSTANTS
///////////////////////////////////////
var DEFAULT_MAX_LENGTH = 80;
var DIGITS = "0123456789";
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
    BaseError.call(this, pos_start, pos_end, "Illegal Character", details);
}

util.inherits(IllegalCharError, BaseError);

function InvalidSyntaxError(pos_start, pos_end, details) {
    BaseError.call(this, pos_start, pos_end, "Invalid Syntax", details);
}

util.inherits(InvalidSyntaxError, BaseError);

function RTError(pos_start, pos_end, details, context) {
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
        result = "\t" + pos.fn + ":" + (pos.ln + 1) + ":" + (pos.col + 1) + ": in " + ctx.display_name + "\n" + result;
        pos = ctx.parent_entry_pos;
        ctx = ctx.parent;
    }

    result = result.slice(0, -1);

    return "stack traceback:\n" + result;
}


///////////////////////////////////////
//UTILITY FUNCTIONS
///////////////////////////////////////
//Module for working with unsigned big integers as strings. 
var ubig = new function () {
    //remove leading zeros, etc.
    function normalize(a) {
        a = "" + a;
        var temp = a.replace(/^0+/, '');
        return (!temp ? "0" : temp);
    }

    //taken from https://codereview.stackexchange.com/questions/92966/multiplying-and-adding-big-numbers-represented-with-strings
    function add(a, b) {
        a = normalize(a);
        b = normalize(b);

        if (parseInt(a) == 0 && parseInt(b) == 0) {
            return '0';
        }

        while (b.length < a.length) {
            b = "0" + b;
        }

        while (a.length < b.length) {
            a = "0" + a;
        }

        // console.log(a,b);


        a = a.split('').reverse();
        b = b.split('').reverse();


        var result = [];

        for (var i = 0; (a[i] >= 0) || (b[i] >= 0); i++) {
            var sum = (parseInt(a[i])) + (parseInt(b[i]));

            if (!result[i]) {
                result[i] = 0;
            }

            var next = parseInt((result[i] + sum) / 10);
            result[i] = (result[i] + sum) % 10;

            if (next) {
                result[i + 1] = next;
            }
        }

        return result.reverse().join('');
    }


    //taken from https://stackoverflow.com/questions/2050111/subtracting-long-numbers-in-javascript
    const subtract = (a, b) => [a, b].map(normalize).map(n => [...n].reverse()).reduce((a, b) => a.reduce((r, d, i) => {
        let s = d - (b[i] || 0)
        if (s < 0) {
            s += 10
            a[i + 1]--
        }
        return '' + s + r
    }, '').replace(/^0+/, ''))


    //taken from https://codereview.stackexchange.com/questions/92966/multiplying-and-adding-big-numbers-represented-with-strings
    function multiply(a, b) {
        a = normalize(a);
        b = normalize(b);

        if (parseInt(a) == 0 || parseInt(b) == 0) {
            return '0';
        }

        a = a.split('').reverse();
        b = b.split('').reverse();
        var result = [];

        for (var i = 0; a[i] >= 0; i++) {
            for (var j = 0; b[j] >= 0; j++) {
                if (!result[i + j]) {
                    result[i + j] = 0;
                }

                result[i + j] += a[i] * b[j];
            }
        }

        for (var i = 0; result[i] >= 0; i++) {
            if (result[i] >= 10) {
                if (!result[i + 1]) {
                    result[i + 1] = 0;
                }

                result[i + 1] += parseInt(result[i] / 10);
                result[i] %= 10;
            }
        }

        return result.reverse().join('');
    }



    function factorial(n) {
        if ((n === 0) || (n === 1))
            return 1;
        else
            return (n * factorial(n - 1));
    }


    //taken from https://locutus.io/php/strings/ord/
    function ord(string) {
        const str = string + ''
        const code = str.charCodeAt(0)
        if (code >= 0xD800 && code <= 0xDBFF) {
            // High surrogate (could change last hex to 0xDB7F to treat
            // high private surrogates as single characters)
            const hi = code
            if (str.length === 1) {
                // This is just a high surrogate with no following low surrogate,
                // so we return its value;
                return code
                // we could also throw an error as it is not a complete character,
                // but someone may want to know
            }
            const low = str.charCodeAt(1)
            return ((hi - 0xD800) * 0x400) + (low - 0xDC00) + 0x10000
        }
        if (code >= 0xDC00 && code <= 0xDFFF) {
            // Low surrogate
            // This is just a low surrogate with no preceding high surrogate,
            // so we return its value;
            return code
            // we could also throw an error as it is not a complete character,
            // but someone may want to know
        }
        return code
    }

    function longDivision(number, divisor) {
        number = normalize(number);
        divisor = parseInt(divisor);
        if (isSmaller(number, "" + divisor)) {
            return "0";
        }

        //As result can be very large store it in string  
        var ans = "";
        //Find prefix of number that is larger than divisor.  
        var idx = 0;
        var temp = ord(number[idx]) - ord('0');
        while (temp < divisor) {
            temp = (temp * 10 + ord(number[idx + 1]) - ord('0'));
            idx += 1;
        }
        idx += 1;

        //Repeatedly divide divisor with temp. After every division, update temp to 
        //include one more digit.  
        while (number.length > idx) {
            //Store result in answer i.e. temp / divisor  
            ans += String.fromCharCode((temp / divisor) + ord('0'));
            //Take next digit of number 
            temp = ((temp % divisor) * 10 + ord(number[idx]) - ord('0'));
            idx += 1;
        }

        ans += String.fromCharCode((temp / divisor) + ord('0'));

        //If divisor is greater than number  
        if (ans.length === 0) {
            return "0";
        }
        //else return ans  
        return ans;
    }

    // Returns true if str1 is smaller than str2.
    function isSmaller(str1, str2) {
        // Calculate lengths of both string
        var n1 = str1.length, n2 = str2.length;
        if (n1 < n2)
            return true;
        if (n2 < n1)
            return false;

        for (var i = 0; i < n1; i++)
            if (str1.charAt(i) < str2.charAt(i))
                return true;
            else if (str1.charAt(i) > str2.charAt(i))
                return false;

        return false;
    }


    this.add = add;
    this.subtract = subtract;
    this.multiply = multiply;
    this.longDivision = longDivision;
    this.isSmaller = isSmaller;
    this.normalize = normalize;
}

//Module for working with signed big integers as strings.
var big = new function () {
    function normalize(a) {
        a = "" + a;
        return copysign(sgn(a), ubig.normalize(abs(a)));
    }

    function sgn(a) {
        return a.charAt(0) === "-" ? -1 : 1;
    }

    function abs(a) {
        return a.charAt(0) === "-" ? a.substring(1) : a;
    }

    function copysign(a, b) {
        return (a === -1 ? neg(b) : b);
    }

    function neg(a) {
        return a.charAt(0) === "-" ? a.substring(1) : "-" + a;
    }

    //Return -1 if x < y, 0 if x == y, 1 if x > y
    function cmp(x, y) {
        switch ([sgn(x), sgn(y)].join(" ")) {
            //Both negative
            case "-1 -1":
                return -cmp(neg(x), neg(y));
            //One negative
            case "-1 1":
                return -1
            //One negative
            case "1 -1":
                return 1
            //Both positive
            case "1 1":
                if (ubig.isSmaller(x, y)) { //less
                    return -1;
                } else if (x === y) { //equal
                    return 0;
                } else { //greater
                    return 1;
                }
        }
    }

    //addition
    function add(x, y) {
        x = normalize(x);
        y = normalize(y);
        //Put the bigger argument first
        if (cmp(x, y) < 0) {
            return add(y, x);
        } else if (abs(y) === "0") {
            return x;
        } else if (cmp(y, "0") < 0) {  // Deal with negative quantities.
            return (cmp(x, "0") >= 0) ? sub(x, neg(y)) : neg(add(neg(y), neg(x)));
        } else {
            // Now it's our main body...
            return ubig.add(x, y);
        }
    }

    //subtraction
    function sub(x, y) {
        x = normalize(x);
        y = normalize(y);

        if (x === y) { //If x == y, return 0
            return "0";
        } else if (cmp(x, y) < 0) { // If x < y then switch place and calculate -(y - x)
            return neg(sub(y, x));
        } else if (abs(x) === "0") {  // If x == 0, return y
            return y;
        } else if (abs(y) === "0") {  // If y == 0, return -x
            return neg(x);
        } else if (cmp(y, "0") < 0) {  // Deal with negative quantities.
            return (cmp(x, "0") >= 0) ? add(x, neg(y)) : sub(neg(y), neg(x));
        } else {
            // Now it's our main body...
            return ubig.subtract(x, y);
        }
    }

    //multiplication
    function mul(x, y) {
        x = normalize(x);
        y = normalize(y);
        if (x === "1") { //If x == 1, return y
            return y;
        } else if (y === "1") { //If y == 1, return x
            return x;
        } else {
            return copysign(sgn(x) * sgn(y), ubig.multiply(abs(x), abs(y)));
        }
    }

    //floor division
    function div(x, y) {
        x = normalize(x);
        y = normalize(y);
        if (x === "1") { //compute reciprocal of y
            if (abs(y) === "0") {
                divisionByZero();
            } else if (cmp(y, "0") < 0) {
                return "-1";
            } else if (y === "1") {
                return "1";
            } else {
                //floor(1/n) for n>1 is always 0
                return "0";
            }
        } else if (y === "1") { //If y == 1, return x
            return x;
        } else if (sgn(x) * sgn(y) === -1) {
            if (mod(abs(x), abs(y)) === "0") {
                return copysign(sgn(x) * sgn(y), ubig.longDivision(abs(x), abs(y)));
            } else {
                return sub(copysign(sgn(x) * sgn(y), ubig.longDivision(abs(x), abs(y))), "1");
            }
        } else {
            return copysign(sgn(x) * sgn(y), ubig.longDivision(abs(x), abs(y)));
        }
    }

    //modulo
    function mod(x, y) {
        return sub(x, mul(div(x, y), y));
    }

    //GCD
    function gcd(a, b) {
        if (abs(b) === "0") {
            return a;
        }

        return gcd(b, mod(a, b));
    }

    this.sgn = sgn;
    this.abs = abs;
    this.cmp = cmp;
    this.neg = neg;
    this.add = add;
    this.sub = sub;
    this.mul = mul;
    this.div = div;
    this.mod = mod;
    this.gcd = gcd;
    this.normalize = normalize;
    this.copysign = copysign;
}



function toInt64(a) {
    if (a instanceof Int64) {
        return a;
    } else if (a instanceof Int32) {
        return toInt64(a.v);
    } else if (typeof a === "string") {
        if (a.charAt(0) === "-") {
            return toInt64(a.substring(1)).mul(new Int64(-1));
        } else {
            var arr = new Array(8);
            arr[0] = big.mod(big.div(big.div(a, 281474976710656), 256), 256);
            arr[1] = big.mod(big.div(a, 281474976710656), 256);
            arr[2] = big.mod(big.div(a, 1099511627776), 256);
            arr[3] = big.mod(big.div(a, 4294967296), 256);
            arr[4] = big.mod(big.div(a, 16777216), 256);
            arr[5] = big.mod(big.div(a, 65536), 256);
            arr[6] = big.mod(big.div(a, 256), 256);
            arr[7] = big.mod(a, 256);

            arr = arr.map((el) => el.charAt(0) === "-" ? el.substring(1) : el);

            return new Int64(Buffer.from(arr.map(parseFloat)));
        }
    } else {
        return new Int64(
            Math.trunc(Math.sign(a) * Math.min(
                Math.abs(a),
                Number.MAX_SAFE_INTEGER
            ))
        );
    }
}

function make_MultilineNode(tmp) {
    if (!(tmp instanceof MultilineNode)) {
        return new MultilineNode([tmp], tmp.pos_start, tmp.pos_end);
    } else {
        return tmp;
    }
}


function isNumber(a) { return typeof a === "number"; }
function toNumber(a) { return isNumber(a) ? a : parseFloat(a); }
function isinstance(a, b) {
    return a.parent === b || (a.parent && isinstance(a.parent, b));
}

function get_display_name(a) {
    return (a ? a.display_name : "" + a) || ("" + a);
}

function get_type(a) {
    // console.log(a.decl_type)
    return a.decl_type || a.parent;
}

function create_int64(a) {
    if (a instanceof BaseObject)
        a = a.value;
    return a instanceof Int32 ? I64.fromNumber(a.toNumber()) : isNumber(a) ? I64.fromNumber(parseFloat(a)) : a;
}

function cons(a, b) {
    var t = add(a.value, b.value).constructor;

    if (t === Int32) return Integer;
    if (t === Int64) return Long;

    return Double;
}

function add(a, b) {
    if (isNumber(a) || isNumber(b)) {
        return toNumber(a) + toNumber(b);
    } else if (b instanceof Int64) {
        return toInt64(a).add(b);
    } else {
        return a instanceof Int64
            ? a.add(toInt64(b))
            : a.add(b);
    }
}

function sub(a, b) {
    if (isNumber(a) || isNumber(b)) {
        return toNumber(a) + toNumber(b);
    } else if (b instanceof Int64) {
        return toInt64(a).add(b);
    } else {
        return a instanceof Int64
            ? a.sub(toInt64(b))
            : a.sub(b);
    }
}

function mul(a, b) {
    if (isNumber(a) || isNumber(b)) {
        return toNumber(a) + toNumber(b);
    } else if (b instanceof Int64) {
        return toInt64(a).add(b);
    } else {
        return a instanceof Int64
            ? a.mul(toInt64(b))
            : a.mul(b);
    }
}

function div(a, b) {
    if (isNumber(a) || isNumber(b)) {
        return toNumber(a) + toNumber(b);
    } else if (b instanceof Int64) {
        return toInt64(a).add(b);
    } else {
        return a instanceof Int64
            ? a.div(toInt64(b))
            : a.div(b);
    }
}


function cmp(a, b) {
    if (isNumber(a) || isNumber(b)) {
        return toNumber(a) < toNumber(b) ? -1 : (toNumber(a) === toNumber(b) ? 0 : 1);
    } else {
        return toInt64(a).compare(toInt64(b));
    }
}

function neg(a) {
    if (isNumber(a)) {
        return -a;
    } else if (a instanceof Int64) {
        return a.mul(new Int64(-1));
    } else {
        return a.mul(-1);
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
    "NEWLINE",
    "INT",
    "LONG",
    "DOUBLE",
    "STRING",
    "IDENTIFIER",
    "KEYWORD",
    "PLUS",
    "MINUS",
    "MUL",
    "DIV",
    "EQ",
    "EE",
    "PE",
    "ME",
    "LPAREN",
    "RPAREN",
    "LCURLY",
    "RCURLY",
    "COMMA",
    "DOT",
    "NE",
    "LT",
    "LTE",
    "GT",
    "GTE",
    "AND",
    "BITAND",
    "OR",
    "BITOR",
    "NOT",
    "EOF"
]);

var KEYWORDS = [
    "do",
    "return",
    "if",
    "else",
    "while",
    "for",
    "const"
];


function Token(type_, value = null, pos_start = null, pos_end = null) {
    if (pos_end === null) pos_end = pos_start !== null ? clone(pos_start).advance() : null;

    this.type = type_;
    this.value = value;
    this.pos_start = pos_start;
    this.pos_end = pos_end;
}

Token.prototype.matches = function (type_, value) {
    return this.type === type_ && this.value === value;
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
        } else if (this.current_char === '"') {
            tokens.push(this.generate_string());
        }  else if (LETTERS.includes(this.current_char)) {
            tokens.push(this.generate_identifier());
        } else if (this.current_char === "+") {
            tokens.push(this.generate_plus());
        } else if (this.current_char === "-") {
            tokens.push(this.generate_minus());
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
        } else if (this.current_char === "{") {
            tokens.push(new Token(TokenType.LCURLY, null, this.pos));
            this.advance();
        } else if (this.current_char === "}") {
            tokens.push(new Token(TokenType.RCURLY, null, this.pos));
            this.advance();
        } else if (this.current_char === ",") {
            tokens.push(new Token(TokenType.COMMA, null, this.pos));
            this.advance();
        } else if (this.current_char === ".") {
            tokens.push(new Token(TokenType.DOT, null, this.pos));
            this.advance();
        } else if (this.current_char === "!") {
            tokens.push(this.generate_not_equals());
        } else if (this.current_char === "=") {
            tokens.push(this.generate_equals());
        } else if (this.current_char === "<") {
            tokens.push(this.generate_less_than());
        } else if (this.current_char === ">") {
            tokens.push(this.generate_greater_than());
        } else if (this.current_char === "&") {
            tokens.push(this.generate_and());
        } else if (this.current_char === "|") {
            tokens.push(this.generate_or());
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
        return new Token(TokenType.LONG, toInt64(num_str), pos_start, this.pos);
    } else {
        return new Token(TokenType.INT, new Int32(num_str), pos_start, this.pos);
    }
}

Lexer.prototype.generate_string = function () {
    var string = "";
    var pos_start = clone(this.pos);
    var escape_character = false;
    this.advance();

    var escape_characters = {
      "n": "\n",
      "t": "\t"
    };

    while(this.current_char !== null && (this.current_char != '"' || escape_character)) {
      if(escape_character) {
        string += escape_characters[this.current_char] || this.current_char;
      } else {
        if(this.current_char == '\\')
          escape_character = true;
        else
          string += this.current_char;
      }

      this.advance()
      escape_character = false;
    }
    
    this.advance();
    return new Token(TokenType.STRING, string, pos_start, this.pos);

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

Lexer.prototype.generate_not_equals = function () {
    var pos_start = clone(this.pos);
    this.advance();

    if (this.current_char === "=") {
        this.advance();
        return new Token(TokenType.NE, pos_start, this.pos);
    } else {
        return new Token(TokenType.NOT, pos_start, this.pos);
    }
}


Lexer.prototype.generate_equals = function () {
    var pos_start = clone(this.pos);
    this.advance();

    if (this.current_char === "=") {
        this.advance();
        return new Token(TokenType.EE, pos_start, this.pos);
    } else {
        return new Token(TokenType.EQ, pos_start, this.pos);
    }
}

Lexer.prototype.generate_less_than = function () {
    var pos_start = clone(this.pos);
    this.advance();

    if (this.current_char === "=") {
        this.advance();
        return new Token(TokenType.LTE, pos_start, this.pos);
    } else {
        return new Token(TokenType.LT, pos_start, this.pos);
    }
}

Lexer.prototype.generate_greater_than = function () {
    var pos_start = clone(this.pos);
    this.advance();

    if (this.current_char === "=") {
        this.advance();
        return new Token(TokenType.GTE, pos_start, this.pos);
    } else {
        return new Token(TokenType.GT, pos_start, this.pos);
    }
}

Lexer.prototype.generate_plus = function () {
    var pos_start = clone(this.pos);
    this.advance();

    if (this.current_char === "=") {
        this.advance();
        return new Token(TokenType.PE, pos_start, this.pos);
    } else {
        return new Token(TokenType.PLUS, pos_start, this.pos);
    }
}


Lexer.prototype.generate_minus = function () {
    var pos_start = clone(this.pos);
    this.advance();

    if (this.current_char === "=") {
        this.advance();
        return new Token(TokenType.ME, pos_start, this.pos);
    } else {
        return new Token(TokenType.MINUS, pos_start, this.pos);
    }
}




Lexer.prototype.generate_and = function () {
    var pos_start = clone(this.pos);
    this.advance();

    if (this.current_char === "&") {
        this.advance();
        return new Token(TokenType.AND, pos_start, this.pos);
    } else {
        return new Token(TokenType.BITAND, pos_start, this.pos);
    }
}

Lexer.prototype.generate_or = function () {
    var pos_start = clone(this.pos);
    this.advance();

    if (this.current_char === "|") {
        this.advance();
        return new Token(TokenType.OR, pos_start, this.pos);
    } else {
        return new Token(TokenType.BITOR, pos_start, this.pos);
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

function StringNode(tok) {
    this.tok = tok;
    this.pos_start = this.tok.pos_start;
    this.pos_end = this.tok.pos_end;
}

NumberNode.prototype.toString = function () { return this.tok.toString(); }


function VarAccessNode(var_name_tok) {
    this.var_name_tok = var_name_tok;
    this.pos_start = this.var_name_tok.pos_start;
    this.pos_end = this.var_name_tok.pos_end;
}

VarAccessNode.prototype.toString = function () { return this.var_name_tok.toString(); }

function VarAssignNode(var_type_tok, var_name_tok, value_node) {
    this.var_type_tok = var_type_tok;
    this.var_name_tok = var_name_tok;
    this.value_node = value_node;

    this.pos_start = this.var_type_tok.pos_start;
    this.pos_end = this.var_name_tok.pos_end;
}


function ConstAssignNode(var_type_tok, var_name_tok, value_node) {
    this.var_type_tok = var_type_tok;
    this.var_name_tok = var_name_tok;
    this.value_node = value_node;

    this.pos_start = this.var_type_tok.pos_start;
    this.pos_end = this.var_name_tok.pos_end;
}

function VarReassignNode(var_name, value_node) {
    this.var_name = var_name;
    this.value_node = value_node;

    this.pos_start = this.var_name.pos_start;
    this.pos_end = this.value_node.pos_end;
}


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

function ReturnNode(node) {
    this.node = node;

    this.pos_start = this.node.pos_start;
    this.pos_end = this.node.pos_end;
}

function BlockNode(node) {
    this.node = node;

    this.pos_start = this.node.pos_start;
    this.pos_end = this.node.pos_end;
}

function IfNode(cond, if_case) {
    this.cond = cond;
    this.if_case = if_case;
    this.pos_start = this.cond.pos_start;
    this.pos_end = this.if_case.pos_end;
}

function IfElseNode(cond, if_case, else_case) {
    this.cond = cond;
    this.if_case = if_case;
    this.else_case = else_case;

    this.pos_start = this.cond.pos_start;
    this.pos_end = this.else_case.pos_end;
}

function DotNode(obj_node, prop_tok) {
    this.obj_node = obj_node;
    this.prop_tok = prop_tok;

    this.pos_start = this.obj_node.pos_start;
    this.pos_end = this.prop_tok.pos_end;
}



function CallNode(node_to_call, arg_nodes) {
    this.node_to_call = node_to_call;
    this.arg_nodes = arg_nodes;

    this.pos_start = this.node_to_call.pos_start;

    if (this.arg_nodes.length > 0)
        this.pos_end = this.arg_nodes[this.arg_nodes.length - 1].pos_end;
    else
        this.pos_end = this.node_to_call.pos_end;
}

function DotAssignNode(obj_node, prop_tok, value_node) {
    this.obj_node = obj_node;
    this.prop_tok = prop_tok;
    this.value_node = value_node;

    this.pos_start = this.obj_node.pos_start;
    this.pos_end = this.value_node.pos_end;
}


function WhileNode(cond, expr) {
    this.cond = cond;
    this.expr = expr;
    this.pos_start = this.cond.pos_start;
    this.pos_end = this.expr.pos_end;
}


function ForNode(expr1, expr2, expr3, body) {
    this.expr1 = expr1;
    this.expr2 = expr2;
    this.expr3 = expr3;
    this.body = body;

    this.pos_start = this.expr1.pos_start;
    this.pos_end = this.body.pos_end;
}

function FuncDeclNode(return_type_tok, var_name_tok, signature, body) {
    this.return_type_tok = return_type_tok;
    this.var_name_tok = var_name_tok;
    this.signature = signature;
    this.body = body;

    this.pos_start = this.return_type_tok.pos_start;
    this.pos_end = this.body.pos_end;
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

Parser.prototype.reverse = function () {
    this.tok_idx--;
    if (this.tok_idx < this.tokens.length && this.tok_idx >= 0) {
        this.current_tok = this.tokens[this.tok_idx];
    }

    return this.current_tok;
}


Parser.prototype.parse = function () {
    var res = this.code();


    if (!res.error && this.current_tok.type !== TokenType.EOF) {
        return res.failure(new InvalidSyntaxError(
            this.current_tok.pos_start, this.current_tok.pos_end,
            "Unexpected T_" + this.current_tok.type
        ))
    }

    return res;
}



Parser.prototype.if_expr = function () {
    var res = new ParseResult();
    res.register(this.advance());

    var cond = res.register(this.expr());
    if (res.error) return res;

    if (this.current_tok.type !== TokenType.LCURLY) {
        return res.failure(new InvalidSyntaxError(
            this.current_tok.pos_start, this.current_tok.pos_end,
            'Expected "{"'
        ));
    }

    res.register(this.advance());
    var tok = this.current_tok;
    if (this.current_tok.type === TokenType.RCURLY) {
        res.register(this.advance());
        return res.success(new IfNode(cond, new MultilineNode(
            [new EmptyNode(tok.pos_start)],
            tok.pos_start,
            tok.pos_start
        )));
    }


    var if_expr = res.register(this.code());
    // console.log(code)
    if (res.error) return res;

    if (this.current_tok.type !== TokenType.RCURLY) {
        return res.failure(new InvalidSyntaxError(
            this.current_tok.pos_start, this.current_tok.pos_end,
            'Expected "}"'
        ));
    }



    res.register(this.advance());
    if (this.current_tok.matches(TokenType.KEYWORD, "else")) {
        res.register(this.advance());
        if (this.current_tok.type !== TokenType.LCURLY) {
            return res.failure(new InvalidSyntaxError(
                this.current_tok.pos_start, this.current_tok.pos_end,
                'Expected "{"'
            ));
        }

        res.register(this.advance());
        var tok = this.current_tok;
        if (this.current_tok.type === TokenType.RCURLY) {
            res.register(this.advance());
            return res.success(new IfElseNode(cond, if_expr, new MultilineNode(
                [new EmptyNode(tok.pos_start)],
                this.current_tok.pos_start,
                this.current_tok.pos_start
            )));
        }


        var else_expr = res.register(this.code());
        if (res.error) return res;

        if (this.current_tok.type !== TokenType.RCURLY) {
            return res.failure(new InvalidSyntaxError(
                this.current_tok.pos_start, this.current_tok.pos_end,
                'Expected "}"'
            ));
        }



        res.register(this.advance());
        return res.success(new IfElseNode(cond, if_expr, else_expr));
    } else {
        return res.success(new IfNode(cond, if_expr));
    }
}

Parser.prototype.for_expr = function () {
    var res = new ParseResult();
    res.register(this.advance());



    if (this.current_tok.type !== TokenType.LPAREN) {
        return res.failure(new InvalidSyntaxError(
            this.current_tok.pos_start, this.current_tok.pos_end,
            'Expected "("'
        ));
    }

    res.register(this.advance());
    var expr1 = res.register(this.expr());
    if (res.error) return res;

    // console.log("stuff", this.current_tok.type)
    if (this.current_tok.type !== TokenType.NEWLINE) {
        return res.failure(new InvalidSyntaxError(
            this.current_tok.pos_start, this.current_tok.pos_end,
            'Expected ";"'
        ));
    }

    res.register(this.advance());
    var expr2 = res.register(this.expr());
    if (res.error) return res;

    // console.log("stuff",this.current_tok.type)
    // res.register(this.advance());
    if (this.current_tok.type !== TokenType.NEWLINE) {
        return res.failure(new InvalidSyntaxError(
            this.current_tok.pos_start, this.current_tok.pos_end,
            'Expected ";"'
        ));
    }

    res.register(this.advance());
    var expr3 = res.register(this.expr());
    if (this.current_tok.type !== TokenType.RPAREN) {
        return res.failure(new InvalidSyntaxError(
            this.current_tok.pos_start, this.current_tok.pos_end,
            'Expected ")"'
        ));
    }

    res.register(this.advance());

    if (this.current_tok.type !== TokenType.LCURLY) {
        return res.failure(new InvalidSyntaxError(
            this.current_tok.pos_start, this.current_tok.pos_end,
            'Expected "{"'
        ));
    }

    res.register(this.advance());
    var body = res.register(this.code());
    if (res.error) return res;

    if (this.current_tok.type !== TokenType.RCURLY) {
        return res.failure(new InvalidSyntaxError(
            this.current_tok.pos_start, this.current_tok.pos_end,
            'Expected "}"'
        ));
    }


    if (res.error) return res;
    res.register(this.advance());
    return res.success(new ForNode(expr1, expr2, expr3, body));
}


Parser.prototype.while_expr = function () {
    var res = new ParseResult();
    res.register(this.advance());


    var cond = res.register(this.expr());
    if (res.error) return res;

    if (this.current_tok.type !== TokenType.LCURLY) {
        return res.failure(new InvalidSyntaxError(
            this.current_tok.pos_start, this.current_tok.pos_end,
            'Expected "{"'
        ));
    }

    res.register(this.advance());
    var tok = this.current_tok;
    if (this.current_tok.type === TokenType.RCURLY) {
        res.register(this.advance());
        return res.success(new IfNode(cond, new MultilineNode(
            [new EmptyNode(tok.pos_start)],
            tok.pos_start,
            tok.pos_start
        )));
    }


    var body = res.register(this.code());
    // console.log(code)
    if (res.error) return res;

    if (this.current_tok.type !== TokenType.RCURLY) {
        return res.failure(new InvalidSyntaxError(
            this.current_tok.pos_start, this.current_tok.pos_end,
            'Expected "}"'
        ));
    }



    res.register(this.advance());
    return res.success(new WhileNode(cond, expr));
}

Parser.prototype.attribute_expr = function () {
    var res = new ParseResult();
    var atom = res.register(this.atom());
    if (res.error) return res;

    var result = atom;
    while (this.current_tok.type === TokenType.DOT) {
        res.register(this.advance());
        if (this.current_tok.type !== TokenType.IDENTIFIER && this.current_tok.type !== TokenType.KEYWORD) {
            return res.failure(new InvalidSyntaxError(
                this.current_tok.pos_start, this.current_tok.pos_end,
                "Expected identifier"
            ));
        }

        var tok = this.current_tok;
        result = new DotNode(result, tok);
        res.register(this.advance());
    }

    return res.success(result);
}

Parser.prototype.call = function () {
    var res = new ParseResult();
    var attribute_expr = res.register(this.attribute_expr());
    if (res.error) return res

    var result = attribute_expr;
    while (this.current_tok.type === TokenType.LPAREN) {
        res.register(this.advance());

        var arg_nodes = []

        if (this.current_tok.type == TokenType.RPAREN) {
            res.register(this.advance());
            attribute_expr = new CallNode(attribute_expr, arg_nodes);
        } else {
            arg_nodes.push(res.register(this.expr()))
            if (res.error) return res;

            while (this.current_tok.type == TokenType.COMMA) {
                res.register(this.advance());

                arg_nodes.push(res.register(this.expr()))
                if (res.error) return res;
            }


            if (this.current_tok.type != TokenType.RPAREN) {
                return res.failure(new InvalidSyntaxError(
                    this.current_tok.pos_start, this.current_tok.pos_end,
                    'Expected "," or ")"'
                ))
            }

            res.register(this.advance());
            attribute_expr = new CallNode(attribute_expr, arg_nodes);
        }
    }

    return res.success(attribute_expr);
}

Parser.prototype.func_decl_expr = function () {
    var res = new ParseResult();
    var return_type_tok = this.current_tok;
    res.register(this.advance());
    var var_name_tok = this.current_tok;
    res.register(this.advance());
    res.register(this.advance());

    var signature = [];
    // res.register(this.advance());
    if (this.current_tok.type !== TokenType.RPAREN) {
        if (this.current_tok.type !== TokenType.IDENTIFIER) {
            return res.failure(new InvalidSyntaxError(
                this.current_tok.pos_start, this.current_tok.pos_end,
                "Expected identifier"
            ));
        }


        var first_arg_type = this.current_tok;

        res.register(this.advance());
        if (this.current_tok.type !== TokenType.IDENTIFIER) {
            return res.failure(new InvalidSyntaxError(
                this.current_tok.pos_start, this.current_tok.pos_end,
                "Expected identifier"
            ));
        }


        var first_arg_name = this.current_tok;

        signature.push([first_arg_type, first_arg_name]);

        res.register(this.advance());
        while (this.current_tok.type === TokenType.COMMA) {
            res.register(this.advance());
            if (this.current_tok.type !== TokenType.IDENTIFIER) {
                return res.failure(new InvalidSyntaxError(
                    this.current_tok.pos_start, this.current_tok.pos_end,
                    "Expected identifier"
                ));
            }

            var arg_type = this.current_tok;

            res.register(this.advance());
            if (this.current_tok.type !== TokenType.IDENTIFIER) {
                return res.failure(new InvalidSyntaxError(
                    this.current_tok.pos_start, this.current_tok.pos_end,
                    "Expected identifier"
                ));
            }


            var arg_name = this.current_tok;

            res.register(this.advance());
            signature.push([arg_type, arg_name]);
        }
    }

    res.register(this.advance());
    if (this.current_tok.type !== TokenType.LCURLY) {
        return res.failure(new InvalidSyntaxError(
            this.current_tok.pos_start, this.current_tok.pos_end,
            'Expected "{"'
        ));
    }

    res.register(this.advance());
    var tok = this.current_tok;
    if (this.current_tok.type === TokenType.RCURLY) {
        res.register(this.advance());
        return res.success(new BlockNode(new MultilineNode(
            [new EmptyNode(tok.pos_start)],
            tok.pos_start,
            tok.pos_start
        )));
    }


    var body = res.register(this.code());
    if (res.error) return res;

    if (this.current_tok.type !== TokenType.RCURLY) {
        return res.failure(new InvalidSyntaxError(
            this.current_tok.pos_start, this.current_tok.pos_end,
            'Expected "}"'
        ));
    }



    res.register(this.advance());
    return res.success(new FuncDeclNode(
        return_type_tok,
        var_name_tok,
        signature,
        body
    ));
}

Parser.prototype.block_expr = function () {
    var res = new ParseResult();

    res.register(this.advance());
    if (this.current_tok.type !== TokenType.LCURLY) {
        return res.failure(new InvalidSyntaxError(
            this.current_tok.pos_start, this.current_tok.pos_end,
            'Expected "{"'
        ));
    }

    res.register(this.advance());
    var tok = this.current_tok;
    if (this.current_tok.type === TokenType.RCURLY) {
        res.register(this.advance());
        return res.success(new BlockNode(new MultilineNode(
            [new EmptyNode(tok.pos_start)],
            tok.pos_start,
            tok.pos_start
        )));
    }


    var code = res.register(this.code());
    if (res.error) return res;

    if (this.current_tok.type !== TokenType.RCURLY) {
        return res.failure(new InvalidSyntaxError(
            this.current_tok.pos_start, this.current_tok.pos_end,
            'Expected "}"'
        ));
    }



    res.register(this.advance());
    return res.success(new BlockNode(code));
}

Parser.prototype.atom = function () {
    var res = new ParseResult();

    var tok = this.current_tok;
    if ([TokenType.PLUS, TokenType.MINUS].includes(tok.type)) {
        res.register(this.advance());
        var attribute_expr = res.register(this.attribute_expr());
        if (res.error) return res;

        return res.success(new UnaryOpNode(tok, attribute_expr));
    } else if (tok.type === TokenType.IDENTIFIER) {
        res.register(this.advance());
        return res.success(new VarAccessNode(tok));
    } else if (tok.type === TokenType.STRING) {
        res.register(this.advance());
        return res.success(new StringNode(tok));
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
    return this.bin_op(this.call, [TokenType.MUL, TokenType.DIV]);
}

Parser.prototype.add_expr = function () {
    return this.bin_op(this.term, [TokenType.PLUS, TokenType.MINUS]);
}


Parser.prototype.comp_expr = function () {
    return this.bin_op(this.add_expr, [TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE]);
}

Parser.prototype.eq_expr = function () {
    return this.bin_op(this.comp_expr, [TokenType.EE, TokenType.NE]);
}


Parser.prototype.bitand_expr = function () {
    return this.bin_op(this.eq_expr, [TokenType.BITAND]);
}

Parser.prototype.bitor_expr = function () {
    return this.bin_op(this.bitand_expr, [TokenType.BITOR]);
}

Parser.prototype.and_expr = function () {
    return this.bin_op(this.bitor_expr, [TokenType.AND]);
}

Parser.prototype.or_expr = function () {
    return this.bin_op(this.and_expr, [TokenType.OR]);
}

Parser.prototype.assignment_expr = function () {
    var res = new ParseResult();
    var var_name = res.register(this.or_expr());
    if (res.error) return res;
    if (this.current_tok.type === TokenType.EQ) {
        res.register(this.advance());
        // res.register(this.advance());

        var expr = res.register(this.expr());
        if (res.error) return res;

        return res.success(new VarReassignNode(var_name, expr));
    }

    return res.success(var_name);
}

Parser.prototype.expr = function () {
    var res = new ParseResult();
    var prev = this.tokens[this.tok_idx - 1];
    var next = this.tokens[this.tok_idx + 1];
    var second_next = this.tokens[this.tok_idx + 2];
    if (this.current_tok.type === TokenType.EOF || this.current_tok.type === TokenType.NEWLINE) {
        return res.success(new EmptyNode(this.pos_start));
    } else if (this.current_tok.matches(TokenType.KEYWORD, "if")) {
        var if_expr = res.register(this.if_expr());
        if (res.error) return res;
        return res.success(if_expr);
    } else if (this.current_tok.matches(TokenType.KEYWORD, "while")) {
        var while_expr = res.register(this.while_expr());
        if (res.error) return res;
        return res.success(while_expr);
    } else if (this.current_tok.matches(TokenType.KEYWORD, "for")) {
        var for_expr = res.register(this.for_expr());
        if (res.error) return res;
        return res.success(for_expr);
    } else if (this.current_tok.matches(TokenType.KEYWORD, "do")) {
        var block_expr = res.register(this.block_expr());
        if (res.error) return res;
        return res.success(block_expr);
    } else if (this.current_tok.matches(TokenType.KEYWORD, "return")) {
        res.register(this.advance());
        var expr = res.register(this.expr());
        if (res.error) return res;
        return res.success(new ReturnNode(expr));
    } else if (this.current_tok.type === TokenType.IDENTIFIER
        && next
        && next.type === TokenType.IDENTIFIER
        && second_next
        && second_next.type === TokenType.LPAREN) {
        var func_decl_expr = res.register(this.func_decl_expr());
        if (res.error) return res;
        return res.success(func_decl_expr);
    } else if (this.current_tok.type === TokenType.IDENTIFIER
        && next
        && next.type === TokenType.IDENTIFIER) {
        var var_type = this.current_tok;

        res.register(this.advance());
        var var_name = this.current_tok;


        res.register(this.advance());

        if (this.current_tok.type !== TokenType.EQ) {
            return res.failure(new InvalidSyntaxError(
                this.current_tok.pos_start, this.current_tok.pos_end,
                'Expected "="'
            ));
        }


        res.register(this.advance());
        var code = res.register(this.expr());
        if (res.error) return res;

        return res.success(new VarAssignNode(var_type, var_name, code));
    } else if (
        this.current_tok.matches(TokenType.KEYWORD, "const")
        && next
        && next.type === TokenType.IDENTIFIER
        && second_next
        && second_next.type === TokenType.IDENTIFIER) {
        res.register(this.advance());
        var var_type = this.current_tok;

        res.register(this.advance());
        var var_name = this.current_tok;


        res.register(this.advance());

        if (this.current_tok.type !== TokenType.EQ) {
            return res.failure(new InvalidSyntaxError(
                this.current_tok.pos_start, this.current_tok.pos_end,
                'Expected "="'
            ));
        }


        res.register(this.advance());
        var code = res.register(this.expr());
        if (res.error) return res;

        return res.success(new ConstAssignNode(var_type, var_name, code));
    }

    return this.bin_op(this.assignment_expr, [TokenType.PE, TokenType.ME]);
}

Parser.prototype.code = function () {
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
            if (res.error) return res;
            if (this.current_tok.type === TokenType.RCURLY) break;
            var line = res.register(this.expr());
            // console.log(res.error ? res.error.details : null);
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
function Int32(v) {
    if (v instanceof Int32)
        this.v = v.v;
    else
        this.v = i32.iadd(v, 0);
}

Int32.prototype.add = function (other) {
    other = new Int32(other);
    return new Int32(i32.iadd(this.v, other.v));
}

Int32.prototype.sub = function (other) {
    other = new Int32(other);
    return new Int32(i32.isub(this.v, other.v));
}

Int32.prototype.mul = function (other) {
    other = new Int32(other);
    return new Int32(i32.imul(this.v, other.v));
}


Int32.prototype.div = function (other) {
    other = new Int32(other);
    return new Int32(i32.idiv(this.v, other.v));
}


Int32.prototype.cmp = function (other) {
    other = new Int32(other);
    return this.v < other.v ? -1 : this.v === other.v ? 0 : 1;
}

Int32.prototype.toString = function () {
    return this.v.toString();
}

function hash(n) {
    return n.toString();
}

function BaseObject(parent = object_meta) {
    this.keys = [];
    this.values = [];
    this.is_const = [];
    this.id = Math.random();
    this.parent = parent;
    this.set_pos();
    this.set_context();
    this.set_decl_type();
}

BaseObject.prototype.set_decl_type = function (decl_type = null) {
    this.decl_type = decl_type;
    return this;
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
    var index = this.keys.indexOf(hash(key));
    if (index === -1) {
        if(typeof key === "object") {
            key.__parent_obj = this;
        }

        this.keys.push(hash(key));
        this.values.push(value);
        this.is_const.push(false);
    } else {
        if(!this.is_const[index]) {
        this.values[index] = value;
        }
    }
}


BaseObject.prototype.set_const = function (key, value) {
    var index = this.keys.indexOf(hash(key));
    if (index === -1) {
        this.keys.push(hash(key));
        this.values.push(value);
        this.is_const.push(true);
    } else {
        if(!this.is_const[index]) {
        this.values[index] = value;
        }
    }
}


BaseObject.prototype.get = function (key) {
    var index = this.keys.indexOf(hash(key));
    if (index === -1 && this.parent) return this.parent.get(key);
    return this.values[index];
}

BaseObject.prototype.get2 = function (key) {
    var index = this.keys.indexOf(hash(key));
    // if (index === -1 && this.parent) return this.parent.get(key);
    return this.values[index];
}


BaseObject.prototype.exists = function (key) {
    var index = this.keys.indexOf(hash(key));
    if (index === -1 && this.parent) return this.parent.exists(key);
    return index > -1;
}

BaseObject.prototype.add = function (other) {
    return [null, this.illegal_operation(other)];
}

BaseObject.prototype.sub = function (other) {
    return [null, this.illegal_operation(other)];
}

BaseObject.prototype.mul = function (other) {
    return [null, this.illegal_operation(other)];
}

BaseObject.prototype.div = function (other) {
    return [null, this.illegal_operation(other)];
}

BaseObject.prototype.neg = function () {
    return [null, this.illegal_operation(this)];
}

BaseObject.prototype.execute = function () {
    return [null, this.illegal_operation(this)];
}

BaseObject.prototype.bitand = function (other) {
    return [null, this.illegal_operation(other)];
}

BaseObject.prototype.bitor = function () {
    return [null, this.illegal_operation(other)];
}

BaseObject.prototype.and = function (other) {
    return [null, this.illegal_operation(other)];
}

BaseObject.prototype.or = function () {
    return [null, this.illegal_operation(other)];
}

BaseObject.prototype.is = function (other) {
    return [new Bool(hash(this) === hash(other)), null];
}

BaseObject.prototype.eq = function (other) {
    return [new Bool(this.id === other.id), null];
}


BaseObject.prototype.ne = function (other) {
    return [new Bool(this.id !== other.id), null];
}

BaseObject.prototype.lt = function (other) {
    return [null, this.illegal_operation(other)];
}

BaseObject.prototype.lte = function (other) {
    return [null, this.illegal_operation(other)];
}

BaseObject.prototype.gt = function (other) {
    return [null, this.illegal_operation(other)];
}

BaseObject.prototype.gte = function (other) {
    return [null, this.illegal_operation(other)];
}

BaseObject.prototype.illegal_operation = function (other) {
    return new RTError(
        this.pos_start, other.pos_end,
        "Illegal operation",
        this.context
    );
}

BaseObject.prototype.toString = function () {
    var k = this.keys;
    var v = this.values;

    return "{" + k.map((el, i) => v[i] === this ? el + ": {...}"
        : el + ": " + v[i]).join(", ") + "}";
}

var object_meta = new BaseObject(null);
object_meta.display_name = "object";

var namespace_meta = new BaseObject(object_meta);
namespace_meta.display_name = "namespace";

var num_meta = new BaseObject(object_meta);
num_meta.display_name = "number";

var int_meta = new BaseObject(num_meta);
int_meta.display_name = "int";

var long_meta = new BaseObject(num_meta);
long_meta.display_name = "long";

var double_meta = new BaseObject(num_meta);
double_meta.display_name = "double";

var void_meta = new BaseObject(object_meta);
void_meta.display_name = "void";

var bool_meta = new BaseObject(object_meta);
bool_meta.display_name = "bool";

var func_meta = new BaseObject(object_meta);
func_meta.display_name = "func";


var string_meta = new BaseObject(object_meta);
string_meta.display_name = "string";


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
    } else {
        return [null, this.illegal_operation(other)];
    }
}

Num.prototype.sub = function (other) {
    if (other instanceof Num) {
        return [new (cons(this, other))(sub(this.value, other.value)), null];
    } else {
        return [null, this.illegal_operation(other)];
    }
}

Num.prototype.mul = function (other) {
    if (other instanceof Num) {
        var old_other = clone(other);
        var result = [new (cons(this, other))(mul(this.value, other.value)), null];
        Object.assign(other, old_other)
        return result;
    } else {
        return [null, this.illegal_operation(other)];
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
    } else {
        return [null, this.illegal_operation(other)];
    }
}

Num.prototype.lt = function (other) {
    return [new Bool(cmp(this, other) < 0), null];
}

Num.prototype.lte = function (other) {
    return [new Bool(cmp(this, other) <= 0), null];
}

Num.prototype.gt = function (other) {
    return [new Bool(cmp(this, other) > 0), null];
}

Num.prototype.gte = function (other) {
    return [new Bool(cmp(this, other) >= 0), null];
}


Num.prototype.eq = function (other) {
    return [new Bool(hash(this) === hash(other)), null];
}

Num.prototype.ne = function (other) {
    return [new Bool(hash(this) !== hash(other)), null];
}

Num.prototype.neg = function () {
    return [new (this.constructor)(neg(this.value)), null];
}

Num.prototype.toString = function () { return this.value.toString(); }



function Integer(value) {
    Num.call(this, new Int32(value));
    this.parent = int_meta;
}

util.inherits(Integer, Num);
Integer.prototype.bitand = function (other) {
    if (other instanceof Integer || other instanceof Long) {
        return [new (cons(this, other))(this.value.and(other.value)), null];
    } else {
        return [null, this.illegal_operation(other)];
    }
}

Integer.prototype.bitor = function (other) {
    if (other instanceof Integer || other instanceof Long) {
        return [new (cons(this, other))(this.value.or(other.value)), null];
    } else {
        return [null, this.illegal_operation(other)];
    }
}


function Long(value) {
    Num.call(this, toInt64(value));
    this.parent = long_meta;
}

util.inherits(Long, Num);
Long.prototype.bitand = function (other) {
    if (other instanceof Integer || other instanceof Long) {
        return [new (cons(this, other))(this.value.and(other.value)), null];
    } else {
        return [null, this.illegal_operation(other)];
    }
}

Long.prototype.bitor = function (other) {
    if (other instanceof Integer || other instanceof Long) {
        return [new (cons(this, other))(this.value.or(other.value)), null];
    } else {
        return [null, this.illegal_operation(other)];
    }
}



function Double(value) {
    Num.call(this, toNumber(value));
    this.parent = double_meta;
}

util.inherits(Double, Num);

function Void() {
    BaseObject.call(this, void_meta);
}

util.inherits(Void, BaseObject);
Void.prototype.eq = function (other) {
    return [new Bool(other instanceof Void), null];
}

Void.prototype.ne = function (other) {
    return [new Bool(!(other instanceof Void)), null];
}


Void.prototype.toString = function () {
    return "VOID";
}

function Bool(value) {
    BaseObject.call(this, bool_meta);
    this.value = value;
}

util.inherits(Bool, BaseObject);
Bool.prototype.and = function (other) {
    if (other instanceof Bool) {
        return [new Bool(this.value && other.value), null];
    } else {
        return [null, this.illegal_operation(other)];
    }
}

Bool.prototype.or = function (other) {
    if (other instanceof Bool) {
        return [new Bool(this.value || other.value), null];
    } else {
        return [null, this.illegal_operation(other)];
    }
}

Bool.prototype.not = function () {
    return [new Bool(!this.value), null];
}

Bool.prototype.toString = function () {
    return this.value.toString();
}

function Func(fn, num_args, name = "<anonymous>", is_method = false) {
    BaseObject.call(this, func_meta);
    this.fn = fn;
    this.num_args = num_args;
    this.name = name;
    this.is_method = is_method;
}

//int sqr(int x) { return x*x; }
//fn([5]) -> [25, null]
//fn([false]) -> [null, <error>]

util.inherits(Func, BaseObject);
Func.prototype.execute = function (args, pos_start, pos_end) {
    if (args.length < this.num_args) {
        return [null, new RTError(
            pos_start, pos_end,
            this.num_args - args.length + " too few arguments passed into " + quote(this.name),
            this.context
        )];
    } else if (args.length > this.num_args) {
        return [null, new RTError(
            pos_start, pos_end,
            args.length - this.num_args + " too many arguments passed into " + quote(this.name),
            this.context
        )];
    } else {
        return this.fn.call(this, args);
    }
}

Func.prototype.toString = function () {
    return "<function " + this.name + ">";
}


function BaseString(str) {
    BaseObject.call(this, string_meta);
    this.str = str;
}

util.inherits(BaseString, BaseObject);
BaseString.prototype.toString = function () {
    return this.str;
}

///////////////////////////////////////
//RUNTIME RESULT
///////////////////////////////////////
function RTResult() {
    this.error = null;
    this.value = null;
}

RTResult.prototype.toArray = function () {
    return [this.value, this.error];
}

RTResult.prototype.register = function (res) {
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
    this.scope = null;
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

Interpreter.prototype.visit_ReturnNode = function (context, node) {
    var res = new RTResult();
    var value = res.register(this.visit(context, node.node));
    if (res.error) return res;
    return Object.assign(value, { "_shouldBeReturned": true });
}

Interpreter.prototype.visit_BlockNode = function (context, node, display_name = "<anonymous closure>") {
    var res = new RTResult();
    var new_context = new Context(display_name, context, node.pos_start);
    new_context.scope = new Namespace(context.scope);

    for (var i = 0; i < node.node.lines.length; i++) {
        if (i >= 1 && node.node.lines[i] instanceof EmptyNode) continue;
        var result = res.register(this.visit(new_context, node.node.lines[i]));
        if (res.error) return res;
        if (result._shouldBeReturned) {
            return res.success(result);
        }
    }

    return res.success(new Void().set_pos(node.pos_start, node.pos_end).set_context(context));
}


Interpreter.prototype.visit_EmptyNode = function (context, node) {
    return new RTResult().success(new Void().set_pos(node.pos_start, node.pos_end).set_context(context));
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
Interpreter.prototype.visit_StringNode = function (context, node) {
    var res = new RTResult();
    return res.success(
            new BaseString(node.tok.value)
                .set_pos(node.tok.pos_start, node.tok.pos_end)
                .set_context(context)
    );
}


Interpreter.prototype.visit_VarAccessNode = function (context, node) {
    var res = new RTResult();

    var var_name = node.var_name_tok.value;
    var value = context.scope.get(var_name);


    if (value == null) {
        return res.failure(new RTError(
            node.pos_start, node.pos_end,
            quote(var_name) + " is not defined.",
            context
        ));
    }

    value.set_pos(node.pos_start, node.pos_end);
    if (!value.context) value.set_context(context);

    return res.success(value);

}

Interpreter.prototype.visit_VarAssignNode = function (context, node) {
    var res = new RTResult();
    var var_name = node.var_name_tok.value;
    var var_type = res.register(this.visit(context, new VarAccessNode(node.var_type_tok)));
    if (res.error) return res;

    var value = res.register(this.visit(context, node.value_node));
    if (res.error) return res;

    var old_value = context.scope.get2(var_name);

    if (old_value != null) {
        return res.failure(new RTError(
            node.pos_start, node.pos_end,
            quote(var_name) + " is already defined.",
            context
        ));
    }

    if (!isinstance(value, var_type)) {
        return res.failure(new RTError(
            node.pos_start, node.pos_end,
            "cannot convert " + get_display_name(get_type(value)) + " to " + get_display_name(var_type),
            context
        ));
    }

    value.set_decl_type(var_type);
    context.scope.set(var_name, value);

    return res.success(value);
}

Interpreter.prototype.visit_ConstAssignNode = function (context, node) {
    var res = new RTResult();
    var var_name = node.var_name_tok.value;
    var var_type = res.register(this.visit(context, new VarAccessNode(node.var_type_tok)));
    if (res.error) return res;

    var value = res.register(this.visit(context, node.value_node));
    if (res.error) return res;

    var old_value = context.scope.get2(var_name);

    if (old_value != null) {
        return res.failure(new RTError(
            node.pos_start, node.pos_end,
            quote(var_name) + " is already defined.",
            context
        ));
    }

    if (!isinstance(value, var_type)) {
        return res.failure(new RTError(
            node.pos_start, node.pos_end,
            "cannot convert " + get_display_name(get_type(value)) + " to " + get_display_name(var_type),
            context
        ));
    }

    value.set_decl_type(var_type);
    context.scope.set_const(var_name, value);

    return res.success(value);
}


Interpreter.prototype.visit_VarReassignNode = function (context, node) {
    var res = new RTResult();


    var value = res.register(this.visit(context, node.value_node));
    if (res.error) return res;

    if (node.var_name instanceof DotNode) {
        var obj = res.register(this.visit(context, node.var_name.obj_node));
        if (res.error) return res;

        var prop = node.var_name.prop_tok.value;
        var old_value = obj.get(prop);

        if (old_value != null) {
            if (!isinstance(value, get_type(old_value))) {
                return res.failure(new RTError(
                    value.pos_start, value.pos_end,
                    "cannot convert " + get_display_name(get_type(value)) + " to " + get_display_name(get_type(old_value)),
                    context
                ));
            } else {
                obj.set(prop, value);
                return res.success(value);
            }
        } else {
            obj.set(prop, value);
            return res.success(value);
        }
    } else {
        if (!(node.var_name instanceof VarAccessNode)) {
            return res.failure(new RTError(
                node.pos_start, node.pos_end,
                "invalid assignment",
                context
            ));
        }


        var var_name = node.var_name.var_name_tok.value;
        var old_value = res.register(this.visit(context, node.var_name));
        if (old_value == null) {
            return res.failure(new RTError(
                node.pos_start, node.pos_end,
                quote(var_name) + " is not defined",
                context
            ));
        }

        //If there is a declaration type stored up, then use that, otherwise look at prototype (parent)
        var var_type = old_value.decl_type || old_value.parent;

        if (!isinstance(value, var_type)) {
            return res.failure(new RTError(
                node.pos_start, node.pos_end,
                "cannot convert " + get_display_name(get_type(value)) + " to " + get_display_name(var_type),
                context
            ));
        }


        value.set_decl_type(var_type);
        value.set_context(old_value.context);
// console.log(old_value.context.scope.keys, old_value.context.scope.is_const)
        old_value.context.scope.set(var_name, value);

        return res.success(value);
    }
}

Interpreter.prototype.visit_BinOpNode = function (context, node) {
    var res = new RTResult();

    var left = res.register(this.visit(context, node.left_node));
    var right = res.register(this.visit(context, node.right_node));

    if (res.error) return res;

    var result, error;
    if (node.op_tok.type === TokenType.PLUS) {
        [result, error] = left.add(right);
    } else if (node.op_tok.type === TokenType.MINUS) {
        [result, error] = left.sub(right);
    } else if (node.op_tok.type === TokenType.MUL) {
        [result, error] = left.mul(right);
    } else if (node.op_tok.type === TokenType.DIV) {
        [result, error] = left.div(right);
    } else if (node.op_tok.type === TokenType.BITAND) {
        [result, error] = left.bitand(right);
    } else if (node.op_tok.type === TokenType.BITOR) {
        [result, error] = left.bitor(right);
    } else if (node.op_tok.type === TokenType.AND) {
        [result, error] = left.and(right);
    } else if (node.op_tok.type === TokenType.OR) {
        [result, error] = left.or(right);
    } else if (node.op_tok.type === TokenType.LT) {
        [result, error] = left.lt(right);
    } else if (node.op_tok.type === TokenType.LTE) {
        [result, error] = left.lte(right);
    } else if (node.op_tok.type === TokenType.EE) {
        [result, error] = left.eq(right);
    } else if (node.op_tok.type === TokenType.NE) {
        [result, error] = left.ne(right);
    } else if (node.op_tok.type === TokenType.GT) {
        [result, error] = left.gt(right);
    } else if (node.op_tok.type === TokenType.GTE) {
        [result, error] = left.gte(right);
    } else if (node.op_tok.type === TokenType.PE) {
        var [result, error] = left.add(right);
        if (error) return res.failure(error);
        Object.assign(left, result.set_pos(node.pos_start, node.pos_end).set_context(context));
    } else if (node.op_tok.type === TokenType.ME) {
        var [result, error] = left.sub(right);
        if (error) return res.failure(error);
        Object.assign(left, result.set_pos(node.pos_start, node.pos_end).set_context(context));
    } else {
        [result, error] = [null, left.illegal_operation(right)];
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


Interpreter.prototype.visit_IfNode = function (context, node) {
    var res = new RTResult();
    var cond = res.register(this.visit(context, node.cond));
    if (res.error) return res;

    if (!isinstance(cond, bool_meta)) {
        return res.failure(new RTError(
            cond.pos_start, cond.pos_end,
            "cannot convert " + get_display_name(get_type(cond)) + " to bool",
            context
        ));
    }

    if (cond.value) {
        var new_context = new Context("if expression", context, node.pos_start);
        new_context.scope = new Namespace(context.scope);

        var if_case = res.register(this.visit(new_context, node.if_case));
        if (res.error) return res;
        return res.success(if_case);
    }

    return res.success(new Void().set_pos(node.pos_start, node.pos_end));
}


Interpreter.prototype.visit_WhileNode = function (context, node) {
    var res = new RTResult();

    var new_context = new Context("while expression", context, node.pos_start);
    new_context.scope = new Namespace(context.scope);

    var accum = [];
    while (true) {
        var cond = res.register(this.visit(new_context, node.cond));
        if (res.error) return res;

        if (!isinstance(cond, bool_meta)) {
            return res.failure(new RTError(
                cond.pos_start, cond.pos_end,
                "cannot convert " + get_display_name(get_type(cond)) + " to bool",
                context
            ));
        }

        if (!cond.value) break;

        var expr = res.register(this.visit(context, node.expr));
        if (res.error) return res;
        accum.push(expr);
    }

    return res.success(accum[accum.length - 1]);
}


Interpreter.prototype.visit_ForNode = function (context, node) {
    var res = new RTResult();

    var new_context = new Context("for expression", context, node.pos_start);
    new_context.scope = new Namespace(context.scope);

    var accum = [];
    res.register(this.visit(new_context, node.expr1));
    if (res.error) return res;


    while (true) {
        var cond = res.register(this.visit(new_context, node.expr2));
        if (res.error) return res;

        if (!isinstance(cond, bool_meta)) {
            return res.failure(new RTError(
                cond.pos_start, cond.pos_end,
                "cannot convert " + get_display_name(get_type(cond)) + " to bool",
                context
            ));
        }

        if (!cond.value) break;

        res.register(this.visit(new_context, node.expr3));
        if (res.error) return res;

        var value = res.register(this.visit(new_context, node.body));
        if (res.error) return res;
        accum.push(value);
    }

    return res.success(accum[accum.length - 1] ? accum[accum.length - 1] : new Void().set_pos(node.pos_start, node.pos_end));
}

Interpreter.prototype.visit_IfElseNode = function (context, node) {
    var res = new RTResult();
    var cond = res.register(this.visit(context, node.cond));
    if (res.error) return res;

    if (!isinstance(cond, bool_meta)) {
        return res.failure(new RTError(
            cond.pos_start, cond.pos_end,
            "cannot convert " + get_display_name(get_type(cond)) + " to bool",
            context
        ));
    }

    if (cond.value) {
        var new_context = new Context("if expression", context, node.pos_start);
        new_context.scope = new Namespace(context.scope);

        var if_case = res.register(this.visit(new_context, node.if_case));
        if (res.error) return res;
        return res.success(if_case);
    } else {
        var new_context = new Context("if expression", context, node.pos_start);
        new_context.scope = new Namespace(context.scope);

        var else_case = res.register(this.visit(new_context, node.else_case));
        if (res.error) return res;
        return res.success(else_case);
    }
}

Interpreter.prototype.visit_FuncDeclNode = function (context, node) {
    var res = new RTResult();
    var self = this;
    var name = node.var_name_tok.value;
    var signature = node.signature;
    //int sqr(int x) { return x*x; }
    //[[Token { value: "int" }, Token { value: "x" } ]]
    var new_context = new Context("function " + quote(name), context, node.pos_start);
    new_context.scope = new Namespace(context.scope);

    var return_type = res.register(this.visit(context, new VarAccessNode(node.return_type_tok)));
    if (res.error) return res;

    for (var i = 0; i < signature.length; i++) {
        res.register(this.visit(context, new VarAccessNode(signature[i][0])));
        if (res.error) return res;
    }


    var func = new Func(function (args) {
        //blah; sqr(2, 3)
        //             ^
        //int sqr(int x) { return x*x;}; sqr()
        //  ^                            

        /*
        <anonymous>:2:1: Runtime Error: 1 too few arguments passed into "sqr"
        stack traceback:
            <anonymous>:2:1 in <program>
        */

        //args = [Integer(2), Integer(3)]

        var num_args = signature.length;

        for (var i = 0; i < num_args; i++) {
            var [arg_type, error] = self.visit(context, new VarAccessNode(signature[i][0])).toArray();
            if (error) return [null, error];

            if (!(isinstance(args[i], arg_type))) {
                return [null, new RTError(
                    args[i].pos_start, args[i].pos_end,
                    "cannot convert " + get_display_name(get_type(args[i])) + " to " + get_display_name(arg_type),
                    context
                )];
            }

            var arg_name = signature[i][1].value;
            new_context.scope.set(arg_name, args[i]);
        }

        var [result, error] = self.visit(new_context, new BlockNode(node.body)).toArray();
        if (error) return [null, error];

        if (!(isinstance(result, return_type))) {
            return [null, new RTError(
                result.pos_start, result.pos_end,
                "cannot convert " + get_display_name(get_type(result)) + " to " + get_display_name(return_type),
                new_context
            )];
        }

        return [result, null];
    }, signature.length, name, signature[0] && signature[0][1] === "this");

    func.set_context(context);
    func.set_pos(node.pos_start, node.pos_end);
    context.scope.set(name, func);

    return res.success(func);
}

Interpreter.prototype.visit_CallNode = function (context, node) {
    var res = new RTResult();
    var value_to_call = res.register(this.visit(context, node.node_to_call));
    if (res.error) return res;

    var args = [];
    for (var i = 0; i < node.arg_nodes.length; i++) {
        var arg = res.register(this.visit(context, node.arg_nodes[i]));
        if (res.error) return res;
        args.push(arg);
    }

    // console.log(value_to_call.is_method, node.node_to_call.constructor.name);
    if(value_to_call.is_method && node.node_to_call instanceof DotNode) {
        var temp = res.register(this.visit(context, node.node_to_call.obj_node));
        if(res.error) return res;
        args.unshift(temp);
    }

    var [result, error] = value_to_call.execute(args, node.pos_start, node.pos_end);
    if (error) return res.failure(error);

    return res.success(result.set_pos(node.pos_start, node.pos_end));
}

Interpreter.prototype.visit_DotNode = function (context, node) {
    var res = new RTResult();

    var obj = res.register(this.visit(context, node.obj_node));
    if (res.error) return res;

    var prop = node.prop_tok.value;
    var result = obj.get(prop);
    if (result == null) {
        return res.success(new Void().set_pos(node.pos_start, node.pos_end).set_context(context));
    } else {
        result.set_pos(node.pos_start, node.pos_end);
        if (!result.context) {
            result.set_context(context);
        }

        // console.log(tmp.context);

        return res.success(result.set_pos(node.pos_start, node.pos_end));

    }
}



///////////////////////////////////////
//RUN
///////////////////////////////////////
var global_scope = new Namespace();
global_scope.set_const("global", global_scope);
global_scope.set_const("true", new Bool(true));
global_scope.set_const("false", new Bool(false));

global_scope.set_const("int", int_meta);
global_scope.set_const("long", long_meta);
global_scope.set_const("double", double_meta);
global_scope.set_const("number", num_meta);
global_scope.set_const("object", object_meta);
global_scope.set_const("void", void_meta);
global_scope.set_const("func", func_meta);
global_scope.set_const("string", string_meta);
global_scope.set_const("VOID", new Void());
global_scope.set_const("bool", bool_meta);
global_scope.set_const("print", new Func(function (args) {
    var a = args[0];
    process.stdout.write("" + a);
    return [new Void(), null];
}, 1, "print"));


global_scope.set_const("println", new Func(function (args) {
    var a = args[0];
    console.log("" + a);
    return [new Void(), null];
}, 1, "println"));

object_meta.set("new", new Func(function (args) {
    var a = args[0];
    return [a, null];
}, 1, "new"));


int_meta.set("new", new Func(function (args) {
    var a = args[0];
    if (isinstance(a, int_meta)) {
        return [a, null];
    } else {
        return [
            null,
            new RTError(
                a.pos_start, a.pos_end,
                "cannot convert " + get_display_name(get_type(a)) + " to int",
                this.context
            )
        ]
    }

}, 1, "new"));

long_meta.set("new", new Func(function (args) {
    var a = args[0];
    if (isinstance(a, long_meta)) {
        return [a, null];
    } else {
        return [
            null,
            new RTError(
                a.pos_start, a.pos_end,
                "cannot convert " + get_display_name(get_type(a)) + " to long",
                this.context
            )
        ]
    }

}, 1, "new"));

double_meta.set("new", new Func(function (args) {
    var a = args[0];
    if (isinstance(a, double_meta)) {
        return [a, null];
    } else {
        return [
            null,
            new RTError(
                a.pos_start, a.pos_end,
                "cannot convert " + get_display_name(get_type(a)) + " to double",
                this.context
            )
        ]
    }

}, 1, "new"));

bool_meta.set("new", new Func(function (args) {
    var a = args[0];
    if (isinstance(a, bool_meta)) {
        return [a, null];
    } else {
        return [
            null,
            new RTError(
                a.pos_start, a.pos_end,
                "cannot convert " + get_display_name(get_type(a)) + " to bool",
                this.context
            )
        ]
    }

}, 1, "new"));



double_meta.set("MIN_VALUE", new Double(Number.MIN_VALUE));
double_meta.set("MAX_VALUE", new Double(Number.MAX_VALUE));
double_meta.set("NEGATIVE_INFINITY", new Double(-Infinity));
double_meta.set("POSITIVE_INFINITY", new Double(+Infinity));
double_meta.set("NaN", new Double(NaN));

void_meta.set("new", new Func(function () { return [new Void(), null]; }, 0, "new"));
func_meta.set("new", new Func(function () {
    return [new Func(function () {
        return [
            new Void().set_pos(this.pos_start, this.pos_end).set_context(this.context),
            null
        ];
    }, 0).set_pos(this.pos_start, this.pos_end).set_context(this.context), null];
}, 0, "new"));

string_meta.set("new", new Func(function (args) {
    var a = args[0];
    if (isinstance(a, string_meta)) {
        return [a, null];
    } else {
        return [
            null,
            new RTError(
                a.pos_start, a.pos_end,
                "cannot convert " + get_display_name(get_type(a)) + " to string",
                this.context
            )
        ]
    }

}, 1, "new"));

string_meta.set("toLowerCase", new Func(function (args) {
    var self = args[0];
    if(!isinstance(self, string_meta)) {
        return [
            null,
            new RTError(
                self.pos_start, self.pos_end,
                "cannot convert "+get_display_name(get_type(self))+" to string",
                this.context
            )
        ];
    }

    return [
        new BaseString(self.str.toLowerCase()),
        null
    ];
}, 1, "toLowerCase", true));


string_meta.set("toUpperCase", new Func(function (args) {
    var self = args[0];
    if(!isinstance(self, string_meta)) {
        return [
            null,
            new RTError(
                self.pos_start, self.pos_end,
                "cannot convert "+get_display_name(get_type(self))+" to string",
                this.context
            )
        ];
    }

    return [
        new BaseString(self.str.toUpperCase()),
        null
    ];
}, 1, "toLowerCase", true));



string_meta.set("length", new Func(function (args) {
    var self = args[0];
    if(!isinstance(self, string_meta)) {
        return [
            null,
            new RTError(
                self.pos_start, self.pos_end,
                "cannot convert "+get_display_name(get_type(self))+" to string",
                this.context
            )
        ];
    }

    return [
        new Integer(new Int32(self.str.length)),
        null
    ];
}, 1, "toLowerCase", true));




string_meta.set("indexOf", new Func(function (args) {
    var [self, str] = args;
    if(!isinstance(self, string_meta)) {
        return [
            null,
            new RTError(
                self.pos_start, self.pos_end,
                "cannot convert "+get_display_name(get_type(self))+" to string",
                this.context
            )
        ];
    }

    if(!isinstance(str, string_meta)) {
        return [
            null,
            new RTError(
                str.pos_start, str.pos_end,
                'cannot convert '+get_display_name(get_type(str))+' to string',
                context
            )
        ];
    }

    return [
        new Integer(new Int32(self.str.indexOf(str.str))),
        null
    ];
}, 2, "indexOf", true));

string_meta.set("lastIndexOf", new Func(function (args) {
    var [self, str] = args;
    if(!isinstance(self, string_meta)) {
        return [
            null,
            new RTError(
                self.pos_start, self.pos_end,
                "cannot convert "+get_display_name(get_type(self))+" to string",
                this.context
            )
        ];
    }

    if(!isinstance(str, string_meta)) {
        return [
            null,
            new RTError(
                str.pos_start, str.pos_end,
                'cannot convert '+get_display_name(get_type(str))+' to string',
                context
            )
        ];
    }

    return [
        new Integer(new Int32(self.str.lastIndexOf(str.str))),
        null
    ];
}, 2, "lastIndexOf", true));




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
    context.scope = global_scope;

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
skink.KEYWORDS = KEYWORDS;
skink.global_scope = global_scope;

module.exports = skink;
