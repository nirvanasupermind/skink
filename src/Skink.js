var Environment = require("./Environment.js");
var lynx = require("lynx-js");
var types = require("./types.js");
// var ArrayList = require("./ArrayList.js");
var fs = require("fs");
var ends = `"'`;
var path = require("path");
var util = require("util");
var assert = require("assert");
var Int = lynx.Int._.int(32);
var Long = lynx.Int;
var NULL = null;

// var yyparse = require("./parser/yyparse.js");

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

let clone = (orig) => Object.assign(Object.create(Object.getPrototypeOf(orig)), orig)
var myGlobal = clone(Environment.GlobalEnvironment);
for(var i = 0; i < Object.keys(types.typeEnv.record).length; i++) {
    myGlobal.define(Object.keys(types.typeEnv.record)[i],Object.values(types.typeEnv.record)[i])
}
/**
 * Skink interpreter.
 */
class Skink {
    constructor(global = myGlobal) {
        this.global = global;
        // this._transformer = new Transformer();
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
        if (this._isInt(exp) || exp instanceof Int || this._isFloat(exp) || exp instanceof Environment) {
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


        // if (exp[0] === 'def') {
        //     exp = this._transformer.transformDefToVarLambda(exp);
        //     return this.eval2(exp, env);
        // }

        // if (exp[0] === "+=") {
        //     exp = this._transformer.transformPlusEquals(exp);
        //     return this.eval2(exp, env, true);
        // }

        // if (exp[0] === "-=") {
        //     exp = this._transformer.transformMinusEquals(exp);
        //     return this.eval2(exp, env, true);
        // }


        // if (exp[0] === "for") {
        //     exp = this._transformer.transformForToWhile(exp);
        //     return this.eval2(exp, env, true);
        // }

        // if (exp[0] === "switch") {
        //     exp = this._transformer.transformSwitchToIf(exp);
        //     return this.eval2(exp, env, true);
        // }





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
            while (Environment.GlobalEnvironment.lookup("__bool")(this.eval2(condition, env))) {
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

        // if (exp[0] === 'import') {
        //     const [_tag, url] = exp;
        //     var thePath = path.join(__dirname, url.slice(1, -1));

        //     var src = fs.readFileSync(thePath, 'utf8')
        //     const body = yyparse.parse(src);
        //     const moduleExp = ["module", "_", body];
        //     this.eval2(["begin", body], env);
        //     return this.eval2(moduleExp, env);
        // }

        // if (exp[0] === 'use') {
        //     var [_tag, url] = exp;
        //     url = this.eval(url, env);
        //     if (typeof url === "string") {
        //         if (!url.includes(".")) {
        //             url += ".skink";
        //         }


        //         url = url.replace(/skink\:/g,
        //             path.join("../sdk/", "./"));
        //         var thePath = path.join(__dirname, url);

        //         var src = fs.readFileSync(thePath, 'utf8')
        //         const body = yyparse.parse(this._preProcess(src));
        //         const moduleExp = ["module", "_", body];
        //         this.eval2(["begin", body], env);
        //         var module = this.eval2(moduleExp, env);
        //         Object.assign(env.record, module.record);
        //         return module;
        //     } else {

        //         var module = url;
        //         Object.assign(env.record, module.record);
        //         return module;
        //     }
        // }



        // --------------------------------------------
        // if-expression:

        if (exp[0] === 'if') {
            const [_tag, condition, consequent, alternate] = exp;
            if (!Environment.GlobalEnvironment.lookup("__bool")(this.eval2(condition, env))) {
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
            args.push(NULL);
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
            return NULL;
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




Skink.Int = Int;
Skink.Long = Long;

module.exports = Skink; 