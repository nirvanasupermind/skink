var Environment = require("./Environment.js");
var Transformer = require("./Transformer.js");
var lynx = require("lynx-js");
var ArrayList = require("./ArrayList.js");
var fs = require("fs");
var ends = `"'`;
var path = require("path");
var util = require("util");
var assert = require("assert");
var yyparse = require("./parser/yyparse.js");

var colors = util.inspect.colors;
function coloredText(x, tint) {
    return `\u001b[${colors[tint][0]}m${x}\u001b[${colors[tint][1]}m`
}

const getCircularReplacer = () => {
    const seen = new WeakSet();
    return (key, value) => {
        if (typeof value === "object" && value !== null) {
            if (seen.has(value)) {
                return;
            }
            seen.add(value);
        }
        return value;
    };
};

// var HashMap = require("./HashMap.js");

///////////////////////////////////////////////////////////////////////

// Turn escaped characters into real ones (e.g. "\\n" becomes "\n").
function interpretEscapes(str) {
    let escapes = {
        b: "\b",
        f: "\f",
        n: "\n",
        r: "\r",
        t: "\t",
    };

    escapes['"'] = '"';

    return str.replace(/\\(u[0-9a-fA-F]{4}|[^u])/g, (_, escape) => {
        let type = escape.charAt(0);
        let hex = escape.slice(1);
        if (type === "u") {
            return String.fromCharCode(parseInt(hex, 16));
        }

        if (escapes.hasOwnProperty(type)) {
            return escapes[type];
        }
        return type;
    });
}




function removeComments(toBeStrippedStr) {
    return toBeStrippedStr.replace(/(^|[^"])\/\*[\s\S]*?\*\//g, "");
}

/**
 * Skink interpreter.
 */
class Skink {
    constructor(global = GlobalEnvironment) {
        this.global = global;
        this._transformer = new Transformer();
    }

    _parseString(exp, env = this.global) {
        return interpretEscapes(exp.slice(1, -1))
            .replace(/\$\{(.*?)\}/g, (a, b) => prettyPrint2(this.eval(b, env)));
    }

    _preProcess(src) {
        src = removeComments(src);
        src = src.replace(/(\b[0-9]+(\.[0-9]+)?(e[+-]?[0-9]+)\b)/g, (_, grp) => (+grp) + "");
        return src;
    }

    eval2(exp, env = this.global) {
        // --------------------------------------------
        // Self-evaluating expressions:
        if (this._isInt(exp) || this._isFloat(exp)) {
            return exp;
        }

        if (this._isString(exp)) {
            // console.log(exp,this._parseString(exp,env));
            return this._parseString(exp, env);
        }

        if (exp == null || exp == "") { return null }


        // --------------------------------------------
        // Block: sequence of expressions

        if (exp[0] === 'begin') {
            const blockEnv = new Environment({}, env);
            return this._evalBlock(exp, blockEnv);
        }


        if (exp[0] === 'def') {
            exp = this._transformer.transformDefToVarLambda(exp);
            return this.eval2(exp, env);
        }

        if (exp[0] === "+=") {
            exp = this._transformer.transformPlusEquals(exp);
            return this.eval2(exp, env, true);
        }

        if (exp[0] === "-=") {
            exp = this._transformer.transformMinusEquals(exp);
            return this.eval2(exp, env, true);
        }


        if (exp[0] === "for") {
            exp = this._transformer.transformForToWhile(exp);
            return this.eval2(exp, env, true);
        }

        if (exp[0] === "switch") {
            exp = this._transformer.transformSwitchToIf(exp);
            return this.eval2(exp, env, true);
        }





        //2. User-defined lambda:
        if (exp[0] === 'lambda') {
            const [_tag, params, body, call] = exp;
            return {
                params,
                body,
                env, // Closure!
            };
        }



        // --------------------------------------------
        // Variable declaration: (var foo 10)
        if (exp[0] === "var") {
            const [_, name, value] = exp;
            return env.define(name, this.eval2(value, env));
        }


        // --------------------------------------------
        // Variable update: (set foo 10)


        if (exp[0] === 'set') {
            // Implement here: see Lectures 6 and 15
            if (exp[1][0] === 'prop') {
                // console.log("***SET");
                // console.log(exp);
                const [_, ref, value] = exp;
                var [_tag, instance, propName] = ref;

                propName = this.eval2(propName, env);
                const instanceEnv = this.eval2(instance, env);
                // name = pretty(this.eval2(name, env));
                // console.log(propName,instanceEnv);
                if (instanceEnv instanceof Environment) {
                    return instanceEnv.define(propName, this.eval2(value, env));
                } else if (instanceEnv instanceof ArrayList) {
                    return instanceEnv.put(propName, this.eval2(value, env));
                }
            }

            return env.assign(exp[1], this.eval2(exp[2], env));
        }

        if (exp[0] === 'prop') {
            var [_tag, instance, name] = exp;
            name = this.eval2(name, env);
            const instanceEnv = this.eval2(instance, env);
            // console.log(name, instanceEnv.record);
            if (instanceEnv instanceof Environment) {
                return instanceEnv.lookup(name);
            } else if (instanceEnv instanceof ArrayList) {
                if (instanceEnv.get(name) === undefined) {
                    return null;
                } else {
                    return instanceEnv.get(name);
                }
            }
        }



        if (exp[0] === 'class') {
            const [_tag, name, parent, body] = exp;
            var parentEnv = this.eval2(parent, env, true);
            if (String(parentEnv) === "null") {
                parentEnv = env;
            }


            var classEnv = new Environment({ "constructor": this.eval2(["lambda", [], body]) }, parentEnv);
            classEnv.__name__ = name;


            this._evalBody(body, classEnv);


            //Class is accesible by name
            return env.define(name, classEnv);

        }

        if (exp[0] === 'super') {
            const [_tag, className] = exp;
            return this.eval2(className, env).parent;
        }

        if (exp[0] === 'while') {
            const [_tag, condition, body] = exp;
            let result;
            while (!this._falsey(this.eval2(condition, env))) {
                result = this.eval2(body, env)
            }
            return result;
        }


        if (exp[0] === 'new') {
            const classEnv = this.eval2(exp[1], env);

            const instanceEnv = new Environment({}, classEnv);

            const args = exp
                .slice(2)
                .map((arg) => this.eval2(arg, env, true))

            this._callUserDefinedFunction(
                classEnv.lookup('constructor'),
                [instanceEnv, ...args]
            )

            return instanceEnv;
        }


        if (exp[0] === 'module') {
            const [_tag, name, body] = exp;
            const moduleEnv = new Environment({}, env);
            this._evalBody(body, moduleEnv);
            this.eval2(["begin", body], env);
            return env.define(name, moduleEnv);
        }

        if (exp[0] === 'import') {
            const [_tag, url] = exp;
            var thePath = path.join(__dirname, url.slice(1, -1));

            var src = fs.readFileSync(thePath, 'utf8')
            const body = yyparse.parse(src);
            const moduleExp = ["module", "_", body];
            this.eval2(["begin", body], env);
            return this.eval2(moduleExp, env);
        }

        if (exp[0] === 'use') {
            var [_tag, url] = exp;
            url = this.eval(url, env);
            if (typeof url === "string") {
                if (!url.includes(".")) {
                    url += ".skink";
                }


                url = url.replace(/skink\:/g,
                    path.join("../sdk/", "./"));
                var thePath = path.join(__dirname, url);

                var src = fs.readFileSync(thePath, 'utf8')
                const body = yyparse.parse(this._preProcess(src));
                const moduleExp = ["module", "_", body];
                this.eval2(["begin", body], env);
                var module = this.eval2(moduleExp, env);
                Object.assign(env.record, module.record);
                return module;
            } else {

                var module = url;
                Object.assign(env.record, module.record);
                return module;
            }
        }



        // --------------------------------------------
        // if-expression:

        if (exp[0] === 'if') {
            const [_tag, condition, consequent, alternate] = exp;
            if (this._falsey(this.eval2(condition, env))) {
                return this.eval2(alternate, env);
            } else {
                return this.eval2(consequent, env);
            }
        }

        // --------------------------------------------
        // Variable access: foo
        if (this._isVariableName(exp)) {
            // console.log(exp,Object.keys(env.record));
            return env.lookup(exp);
        }

        // --------------------------------------------
        // Function calls:
        //
        // (print "Hello World")
        // (+ x 5)
        // (> foo bar)

        if (Array.isArray(exp)) {
            const fn = this.eval2(exp[0], env);
            const args = exp.slice(1).map(arg => this.eval2(arg, env));

            // 1. Native function:

            // See Lecture 10

            if (typeof fn === 'function') {
                var t1 = fn(...args);
                if (t1 === undefined) {
                    return null;
                } else {
                    return t1;
                }
            }

            // 2. User-defined function:


            return this._callUserDefinedFunction(fn, args);
        }

        throw "Unimplemented " + JSON.stringify(exp);
    }

    _callUserDefinedFunction(fn, args) {
        // console.log(fn, args);
        while (args.length < fn.params.length) {
            args.push(null);
        }

        const activationRecord = {};
        fn.params.forEach((param, index) => {
            activationRecord[param] = args[index];
        })

        const activationEnv = new Environment(
            activationRecord,
            fn.env //Static scope!
        );

        var t1 = this._evalBody(fn.body, activationEnv);
        if (t1 === undefined) {
            return null;
        } else {
            return t1;
        }
    }

    _evalBody(body, env) {
        if (body == null) { return null }
        if (body[0] === 'begin') {
            return this._evalBlock(body, env);
        }
        return this.eval2(body, env);
    }

    eval(exp, env) {
        // console.log("**",exp);
        exp = yyparse.parse(this._preProcess(exp));
        var t1 = this.eval2(exp, env)
        return t1;
    }

    evalFile(exp, env) {
        // console.log("dir:"+__dirname);
        exp = "" + fs.readFileSync(path.join(__dirname, exp));
        return this.eval(exp, env);
    }


    _evalBlock(block, env) {
        let result;
        const [_tag, ...expressions] = block;
        expressions.forEach(exp => {
            result = this.eval2(exp, env);
        });

        if (result === undefined) {
            result = null;
        }

        return result;
    }


    _isInt(exp) {
        return exp instanceof lynx.Int;
    }

    _isFloat(exp) {
        return typeof exp === 'number';
    }

    _isString(exp) {
        return typeof exp === 'string'
            && exp.charAt(0) === '"'
            && exp.slice(-1) === '"'
            || (typeof exp === 'string'
                && exp.charAt(0) === "'"
                && exp.slice(-1) === "'")
    }

    _isVariableName(exp) {
        return typeof exp === 'string' && /^[+\-*/%<>=a-zA-Z0-9_\!\&\|]+$/.test(exp);
    }


    _falsey(exp) {
        return !exp || (String(exp) === "0" && exp !== "0") || (exp instanceof Environment && exp.has("bool") &&
            this._callUserDefinedFunction(exp.lookup("bool"), []) === false);
    }
}

function getInstanceType(obj) {
    if (obj == null) { return "Null" }
    return obj.constructor.name;
}


function getInstanceTypes(obj) {
    return "" + getInstanceType(...obj);
}

function binOp(A, B) {
    return function (op1, op2) {
        var skink = new Skink();
        if (op1 instanceof Environment && op1.has(B)) {
            return skink._callUserDefinedFunction(op1.lookup(B), [op2]);
        } else if (!(op1 instanceof lynx.Int)
            || !(op2 instanceof lynx.Int)) {
            return A(Number.parseFloat(op1), Number.parseFloat(op2));
        } else {
            return op1[B](op2);
        }
    }
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

function mathTemplate(fn, delegate) {
    return (...x) => {
        if (delegate && x[0] instanceof Environment
            && x[0].has(delegate)) {
            return new Skink()._callUserDefinedFunction(x[0].lookup(delegate), x.slice(1))
        } else {
            return fn(...x.map(Number.parseFloat));
        }
    };
}

function logBase(x, b = Math.E) {
    return Math.log(x) / Math.log(b);
}

//taken from https://stackoverflow.com/questions/3108986/gaussian-bankers-rounding-in-javascript
function evenRound(num, decimalPlaces) {
    var d = decimalPlaces || 0;
    var m = Math.pow(10, d);
    var n = +(d ? num * m : num).toFixed(8); // Avoid rounding errors
    var i = Math.floor(n), f = n - i;
    var e = 1e-8; // Allow for rounding errors in f
    var r = (f > 0.5 - e && f < 0.5 + e) ?
        ((i % 2 == 0) ? i : i + 1) : Math.round(n);
    return d ? r / m : r;
}


var factorial = (function () {
    var cache = {},
        fn = function (n) {
            if ("" + n === "0") {
                return 1;
            } else if (cache[n]) {
                return cache[n];
            }
            return cache[n] = n.mul(fn(n.sub(1)));
        };

    return fn;
})();

var GlobalEnvironment = new Environment({
    "opts": new Environment({"colors":false}),
    "null": null,
    "true": true,
    "false": false,
    "Infinity": Infinity,
    "NaN": NaN,
    "assert": (a) => assert(!new Skink()._falsey(a)),
    "parseInt": (...args) => lynx.Int(...args),
    "parseFloat": Number.parseFloat,
    "Math": new Environment({
        "E": Math.E,
        "PI": Math.PI,
        "TAU": 2 * Math.PI,
        "sin": mathTemplate(Math.sin, "sin"),
        "cos": mathTemplate(Math.cos, "cos"),
        "tan": mathTemplate(Math.tan, "tan"),
        "asin": mathTemplate(Math.asin, "asin"),
        "acos": mathTemplate(Math.acos, "acos"),
        "atan": mathTemplate(Math.atan, "atan"),
        "atan2": mathTemplate(Math.atan2, "atan2"),
        "exp": mathTemplate(Math.exp, "exp"),
        "log": mathTemplate(logBase, "log"),
        "sqrt": mathTemplate(Math.sqrt, "sqrt"),
        pow(x, y) {
            if (x instanceof lynx.Int && y instanceof lynx.Int) {
                return x.pow(y);
            } else {
                return mathTemplate(Math.pow, "pow");
            }
        },
        "ceil": mathTemplate(Math.ceil, "ceil"),
        "floor": mathTemplate(Math.floor, "floor"),
        "rint": mathTemplate(evenRound, "rint"),
        "round": mathTemplate((a) => new lynx.Int(Math.round(a)), "round"),
        "sign": mathTemplate(Math.sign, "sign"),
        factorial(a) {
            if (a instanceof lynx.Int) {
                return factorial(a);
            } else {
                return mathTemplate(lynx.fac, "fac")(a);
            }
        },
        "random": Math.random,
        abs(a) {
            if (a instanceof lynx.Int) {
                return a.abs();
            } else {
                return mathTemplate(Math.abs)(a);
            }
        },
        min(a, b) {
            if (a instanceof lynx.Int && b instanceof lynx.Int) {
                return (a.compareTo(b) === -1 ? a : b);
            } else {
                return mathTemplate(Math.min)(a, b);
            }
        },
        max(a, b) {
            if (a instanceof lynx.Int && b instanceof lynx.Int) {
                return (a.compareTo(b) === 1 ? a : b);
            } else {
                return mathTemplate(Math.max)(a, b);
            }
        }
    }),
    "clone": Environment.clone,
    "ord": (a) => new lynx.Int(ord(a)),
    "+": binOp((a, b) => a + b, "add"),
    "-"(a, b = null) {
        if (b === null)
            return binOp((a, b) => -a, "neg")(a);
        return binOp((a, b) => a - b, "sub")(a, b);
    },
    "*": binOp((a, b) => a * b, "mul"),
    "/": binOp((a, b) => a / b, "div"),
    "%": binOp((a, b) => a % b, "mod"),
    "&": binOp((a, b) => a & b, "bitwise_and"),
    "|": binOp((a, b) => a | b, "bitwise_or"),
    "&&": (a, b) => !(new Skink()._falsey(a))
        && !(new Skink()._falsey(b)),
    "||": (a, b) => !(new Skink()._falsey(a))
        || !(new Skink()._falsey(b)),
    "!": new Skink()._falsey,
    "<"(op1, op2) {
        var skink = new Skink();
        if (typeof op1 === "string" && typeof op2 === "string") {
            return op1.localeCompare(op2) < 0;
        } else if (op1 instanceof Environment && op1.has("lt")) {
            return skink._callUserDefinedFunction(op1.lookup("lt"), [op2]);
        } else if (!(op1 instanceof lynx.Int)) {
            return Number.parseFloat(op1) < Number.parseFloat(op2);
        } else {
            return op1.compareTo(op2) < 0;
        }
    },
    ">"(op1, op2) {
        var skink = new Skink();
        if (typeof op1 === "string" && typeof op2 === "string") {
            return op1.localeCompare(op2) > 0;
        } else if (op1 instanceof Environment && op1.has("gt")) {
            return skink._callUserDefinedFunction(op1.lookup("gt"), [op2]);
        } else if (!(op1 instanceof lynx.Int)) {
            return Number.parseFloat(op1) > Number.parseFloat(op2);
        } else {
            return op1.compareTo(op2) > 0;
        }
    },
    "<="(op1, op2) {
        if (op1 instanceof Environment && op1.has("le")) {
            return skink._callUserDefinedFunction(op1.lookup("le"), [op2]);
        } else {
            return !(GlobalEnvironment.lookup(">")(op1, op2));
        }
    },
    ">="(op1, op2) {
        if (op1 instanceof Environment && op1.has("ge")) {
            return skink._callUserDefinedFunction(op1.lookup("ge"), [op2]);
        } else {
            return !(GlobalEnvironment.lookup("<")(op1, op2));
        }
    },

    "="(op1, op2) {
        if (typeof op1 === "object" || typeof op2 === "object") {
            return S(op1) === S(op2);
        } else {
            return op1 === op2;
        }
    },
    print(...args) {
        // console.log(args[0]);
        console.log(...args.map(prettyPrint));
    },
    list(...args) {
        return new ArrayList(args);
    },
    add(x, y) {
        return x.add(y);
    },
    remove(x, y) {
        x.remove(Number.parseFloat(y));
    },
    len(x) {
        var skink = new Skink();
        var type = GlobalEnvironment.lookup("type");
        var result;
        if (x instanceof ArrayList) {
            result = x.value.length;
        } else if (typeof x === "string") {
            result = x.length;
        } else if (x instanceof Environment && x.has("length")) {
            result = skink._callUserDefinedFunction(x.lookup("length"), []);
        } else {
            throw new Error(`object of type "${type(x)}" has no len()`)
        }

        return new lynx.Int(result);
    },
    split(x, y) {
        return new ArrayList(x.split(y));
    },
    join(x, y) {
        return new ArrayList(x.join(""));
    },
    type(x) {
        switch (getInstanceType(x)) {
            case "Number": return "Float"
            case "Environment":
                if (x.parent && x.parent.__name__) {
                    return x.parent.__name__;
                } else {
                    return "Environment"
                }
            default: return getInstanceType(x)


        }
    },
    map(x, y) {
        var skink = new Skink();
        var fn;
        if (typeof y !== "function") {
            fn = (...args) => skink._callUserDefinedFunction(y, args);
        } else {
            fn = y;
        }

        return new ArrayList(x.value.map(fn));
    },
    indexOf(x, y) {
        if (typeof x === "string") { //string
            if (x.indexOf(y) === -1) {
                return null;
            } else {
                return new lynx.Int(x.indexOf(y));
            }
        } else { //ArrayList
            if (x.value.map(S).indexOf(S(y)) === -1) {
                return null;
            } else {
                return new lynx.Int(x.value.map(S).indexOf(S(y)));
            }
        }
    },
    slice(x, y, z = null) {
        if (z === null) { z = (x.length ? x.length : x.value.length) }
        if (x instanceof ArrayList) {
            return new ArrayList(x.value.slice(Number.parseFloat(y), Number.parseFloat(z)));
        } else {
            return x.slice(Number.parseFloat(y), Number.parseFloat(z));
        }
    },
    charAt(x, y) {
        y = new ArrayList(x.split(""))._negIndex(y);
        return x.charAt(y);
    }
});

function S(x) {
    return getInstanceType(x) + " " + JSON.pruned(x);
}


function prettyPrint(x) {
    let opts = { depth: null, colors: "auto" };
    let s = util.inspect(x, opts);
    return JSON.stringify(s);
}

!function () { "use strict"; var t; Date.prototype.toPrunedJSON = Date.prototype.toJSON, String.prototype.toPrunedJSON = String.prototype.toJSON; var r = /[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g, e = { "\b": "\\b", "\t": "\\t", "\n": "\\n", "\f": "\\f", "\r": "\\r", '"': '\\"', "\\": "\\\\" }; function n(t) { return r.lastIndex = 0, r.test(t) ? '"' + t.replace(r, function (t) { var r = e[t]; return "string" == typeof r ? r : "\\u" + ("0000" + t.charCodeAt(0).toString(16)).slice(-4) }) + '"' : '"' + t + '"' } JSON.pruned2 = function (r, e, o) { return t = [], function r(e, o, u, f) { var i, c, l, a, p, s = o[e]; if (s && !(s instanceof Environment) && "function" == typeof s.toPrunedJSON) return s.toPrunedJSON(e); switch (typeof s) { case "string": return n(s); case "number": return isFinite(s) ? String(s) : "null"; case "boolean": case "null": return "null"; case "object": if (!s) return "null"; if (u <= 0 || -1 !== t.indexOf(s)) return '-pruned-'.toPrunedJSON(); if (t.push(s), p = [], "[object Array]" === Object.prototype.toString.apply(s)) { for (a = Math.min(s.length, f), i = 0; i < a; i += 1)p[i] = r(i, s, u - 1, f) || "null"; return l = 0 === p.length ? "[]" : "[" + p.join(",") + "]" } for (c in s) if (Object.prototype.hasOwnProperty.call(s, c)) try { (l = r(c, s, u - 1, f)) && p.push(n(c) + ":" + l) } catch (t) { } return l = 0 === p.length ? "{}" : "{" + p.join(",") + "}" } }("", { "": r }, e = e || 6, o = o || 50) } }();
!function () { "use strict"; var t; Date.prototype.toPrunedJSON2 = Date.prototype.toJSON, String.prototype.toPrunedJSON2 = String.prototype.toJSON; var r = /[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g, n = { "\b": "\\b", "\t": "\\t", "\n": "\\n", "\f": "\\f", "\r": "\\r", '"': '\\"', "\\": "\\\\" }; function e(t) { return r.lastIndex = 0, r.test(t) ? '"' + t.replace(r, function (t) { var r = n[t]; return "string" == typeof r ? r : "\\u" + ("0000" + t.charCodeAt(0).toString(16)).slice(-4) }) + '"' : '"' + t + '"' } JSON.pruned3 = function (r, n, u) { return t = [], function r(n, u, o, f) { var i, c, p, a, l, s = u[n]; if (s && "function" == typeof s.toPrunedJSON2) return s.toPrunedJSON2(n); switch (typeof s) { case "string": return e(s); case "number": return isFinite(s) ? String(s) : "null"; case "boolean": case "null": return String(s); case "object": if (!s) return "null"; if (o <= 0 || -1 !== t.indexOf(s)) return '"-pruned-"'; if (t.push(s), l = [], "[object Array]" === Object.prototype.toString.apply(s)) { for (a = Math.min(s.length, f), i = 0; i < a; i += 1)l[i] = r(i, s, o - 1, f) || "null"; return p = 0 === l.length ? "[]" : "[" + l.join(",") + "]" } for (c in s) if (Object.prototype.hasOwnProperty.call(s, c)) try { (p = r(c, s, o - 1, f)) && l.push(e(c) + ":" + p) } catch (t) { } return p = 0 === l.length ? "{}" : "{" + l.join(",") + "}" } }("", { "": r }, n = n || 6, u = u || 50) } }();
// JSON.pruned : a function to stringify any object without overflow
// example : var json = JSON.pruned({a:'e', c:[1,2,{d:{e:42, f:'deep'}}]})
// two additional optional parameters :
//   - the maximal depth (default : 6)
//   - the maximal length of arrays (default : 50)
// GitHub : https://github.com/Canop/JSON.prune
// This is based on Douglas Crockford's code ( https://github.com/douglascrockford/JSON-js/blob/master/json2.js )
(function () {
    'use strict';

    var DEFAULT_MAX_DEPTH = 6;
    var DEFAULT_ARRAY_MAX_LENGTH = 50;
    var seen; // Same variable used for all stringifications

    Date.prototype.toPrunedJSON = Date.prototype.toJSON;
    String.prototype.toPrunedJSON = function () {
        return coloredText(JSON.stringify(this), "green");
    }

    lynx.Int.prototype.toPrunedJSON = function () {
        return coloredText(String(this), "blue");
    }

    Number.prototype.toPrunedJSON = function () {
        return coloredText(String(this), "yellow");
    }

    Environment.prototype.toPrunedJSON = function () {
        if (this.has("toString")) {
            return new Skink()._callUserDefinedFunction(this.lookup("toString"), []);
        } else {
            return '{"record":' + JSON.pruned2(this.record) + "}";
        }
    }

    ArrayList.prototype.toPrunedJSON = function () {
        if (this.value.length > DEFAULT_ARRAY_MAX_LENGTH)
            return JSON.pruned(this.value.slice(0, DEFAULT_ARRAY_MAX_LENGTH - 1).concat('-truncated-'))
        return JSON.pruned(this.value);
    }

    Number.prototype.toPrunedJSON = function () {
        return util.inspect(this, { depth: null, colors: "auto" });
    }

    Function.prototype.toPrunedJSON = function () {
        return util.inspect(this, { depth: null, colors: "auto" });
    }

    Boolean.prototype.toPrunedJSON = function () {
        return util.inspect(this, { depth: null, colors: "auto" });
    }

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
        if (value && typeof value.toPrunedJSON === 'function') {
            return value.toPrunedJSON(key);
        }

        switch (typeof value) {
            case 'string':
                return quote(value);
            case 'number':
                return isFinite(value) ? value.toPrunedJSON() : "null";
            case 'boolean':
            case 'null':
                return String(value);
            case 'object':
                if (!value) {
                    return "null";
                }
                if (depthDecr <= 0 || seen.indexOf(value) !== -1) {
                    return '"-pruned"'.toPrunedJSON();
                }

                seen.push(value);
                partial = [];
                if (Object.prototype.toString.apply(value) === '[object Array]') {
                    length = Math.min(value.length, arrayMaxLength);
                    for (i = 0; i < length; i += 1) {
                        partial[i] = str(i, value, depthDecr - 1, arrayMaxLength) || "null";
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
        if (value == null) {
            return "null";
        }

        if (value != null && typeof value.toPrunedJSON === 'function') {
            return value.toPrunedJSON();
        }

        seen = [];
        depthDecr = depthDecr || DEFAULT_MAX_DEPTH;
        arrayMaxLength = arrayMaxLength || DEFAULT_ARRAY_MAX_LENGTH;
        return str('', { '': value }, depthDecr, arrayMaxLength);
    };

}());



function prettyPrint(x) {
    if (GlobalEnvironment.lookup("opts").lookup("colors")) {
        var skink = new Skink();
        if (typeof x === "string" || x == null) {
            return "" + x;
        } else if (x instanceof Environment && x.has("toString")) {
            return prettyPrint(skink._callUserDefinedFunction(x.lookup("toString"), x));
        } else {
            return JSON.pruned(x);
        }
    } else {
        return prettyPrint2(x);
    }
}

lynx.Int.prototype.toPrunedJSON2 = function () {
    return this.toString();
}

Function.prototype.toPrunedJSON2 = function () {
    return util.inspect(this);
}

ArrayList.prototype.toPrunedJSON2 = function () {
    return JSON.pruned3(this.value);
}

function prettyPrint2(x) {
    var skink = new Skink();
    if (typeof x === "string" || x == null) {
        return "" + x;
    } else if (x instanceof Environment && x.has("toString")) {
        return prettyPrint(skink._callUserDefinedFunction(x.lookup("toString"), x));
    } else {
        return JSON.pruned3(x);
    }
}

Skink.prettyPrint = prettyPrint;
module.exports = Skink; 