/* 
This module is the main entry-point for our application. 
It implements the interpreter for the language.
*/
var types = require("./types.js");
var assert = require("assert");
var Environment = require("./Environment.js");
var yyparse = require("./parser/skinkParser.js");
var Transformer = require("./Transformer.js")
var fs = require("fs");
var path = require("path");
var util = require("util");

var TRIM = 2 / 5;
var MAX_LEN = 200;

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

function getClass(obj) {
    if (obj == null) {
        return "Null";
    }

    var funcNameRegex = /function (.{1,})\(/;
    var results = (funcNameRegex).exec((obj).constructor.toString());
    return (results && results.length > 1) ? results[1] : "";
};



function removeComments(toBeStrippedStr) {
    return toBeStrippedStr.replace(/(^|[^"])\/\*[\s\S]*?\*\//g, "");
}

function parseDouble(toBeStrippedStr) {
    return parseFloat(prettyPrint(toBeStrippedStr));
}

String.prototype.repeat2 = function (a) {
    if (a <= 0)
        return ""
    return this.repeat(a);
}

function convertSciToStandard(a) {
    return Number(a).toString();
}



/**
 * Skink interpreter.
 */
class Skink {
    /**
     * Creates a Skink instance with the global environment.
     * @param {*} global 
     */
    constructor(global = GlobalEnvironment) {
        this.global = global;
        this._transformer = new Transformer();
        this.count = 0;
    }

    _preProcess(exp) {
        exp = removeComments(exp);
        exp = exp.replace(/(\b[0-9]+(\.[0-9]+)?(e[+-]?[0-9]+)\b)/g, function (_, grp) {
            // console.log("2", arguments);

            // if (!(convertSciToStandard(grp).includes("."))) {
            //     return convertSciToStandard(grp) + ".0";
            // }
            return convertSciToStandard(grp);
        });

        return exp;
    }

    eval(exp, env) {
        exp = yyparse.parse(this._preProcess(exp));
        return this.eval2(exp, env);
    }


    eval2(exp, env = this.global) {
        this.count++;
        if (exp === undefined)
            return null
        // --------------------------------------------
        // Self-evaluating expressions:

        if (getClass(exp) === "Int" || getClass(exp) === "Long" || this._isNumber(exp)) {
            return exp;
        }

        if (this._isString(exp)) {
            return exp.slice(1, -1).replace(/\\u([0-9a-f][0-9a-f][0-9a-f][0-9a-f])/gi, (a, b) => {
                return String.fromCharCode(parseInt(b, 16))
            });
        }





        // --------------------------------------------
        // Block: sequence of expressions

        if (exp[0] === "begin") {
            return this._evalBlock(exp, env);
        }



        // --------------------------------------------
        // Variable declaration: (var foo 10)
        if (exp[0] === "var") {
            const [_, name, value] = exp;
            return env.define(name, this.eval2(value, env));
        }

        if (exp[0] === 'prop') {
            var [_tag, instance, name] = exp;
            name = String(this.eval2(name, env));
            const instanceEnv = this.eval2(instance, env);
            return instanceEnv.lookup(name);
        }

        if (exp[0] === 'module') {
            const [_tag, name, body] = exp;
            const moduleEnv = new Environment({}, env);
            this._evalBody(body, moduleEnv);
            return env.define(name, moduleEnv);
        }

        if (exp[0] === 'import') {
            const [_tag, url] = exp;
            var thePath = path.join(__dirname, url.slice(1, -1));

            var src = fs.readFileSync(thePath, 'utf8')
            const body = yyparse.parse(src);
            const moduleExp = ["module", "_", body];
            return this.eval2(moduleExp, env);
        }

        if (exp[0] === 'using') {
            var [_tag, url] = exp;
            url = this.eval(url, env);
            if (typeof url === "string") {
                if (!url.includes(".")) {
                    url += ".skink";
                }


                url = url.replace(/skink\:/g,
                    path.join("../lib/", "./"));
                var thePath = path.join(__dirname, url);

                var src = fs.readFileSync(thePath, 'utf8')
                const body = yyparse.parse(this._preProcess(src));
                const moduleExp = ["module", "_", body];
                var module = this.eval2(moduleExp, env);
                Object.assign(env.record, module.record);
                return module;
            } else {

                var module = url;
                Object.assign(env.record, module.record);
                return module;
            }
        }



        if (this._isVariableName(exp)) {
            // console.log(exp,Object.keys(env.record));
            return env.lookup(exp);
        }

        // --------------------------------------------
        // Variable update: (set foo 10)
        if (exp[0] === 'set') {
            if (exp[1][0] === 'prop') {
                // console.log(exp);
                const [_, ref, value] = exp;
                var [_tag, instance, propName] = ref;
                if (typeof propName === "string") {
                    propName = propName.slice(1, -1);
                }

                // propName = JSON.stringify(this.eval(propName, env), types.getCircularReplacer());
                const instanceEnv = this.eval(instance, env);
                // console.log(value,env.record.value);
                return instanceEnv.define(propName, this.eval2(value, env));
            }

            return env.assign(exp[1], this.eval2(exp[2], env));
        }

        if (exp[0] === 'class') {
            const [_tag, name, parent, body] = exp;
            var parentEnv = this.eval2(parent, env, true);
            if (String(parentEnv) === "null") {
                parentEnv = env;
            }


            var classEnv = new Environment({}, parentEnv);
            classEnv.__name__ = name;


            this._evalBody(body, classEnv);


            //Class is accesible by name
            return env.define(name, classEnv);

        }

        if (exp[0] === 'super') {
            const [_tag, className] = exp;
            return this.eval2(className, env).parent;
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


        if (exp[0] === "for") {
            exp = this._transformer.transformForToWhile(exp);
            return this.eval2(exp, env, true);
        }

        if (exp[0] === "+=") {
            exp = this._transformer.transformPlusEquals(exp);
            return this.eval2(exp, env, true);
        }

         if (exp[0] === "-=") {
            exp = this._transformer.transformMinusEquals(exp);
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

        if (exp[0] === 'def') {
            exp = this._transformer.transformDefToVarLambda(exp);
            return this.eval2(exp, env);
        }



        if (exp[0] === 'while') {
            const [_tag, condition, body] = exp;
            let result;
            while (!this._falsey(this.eval2(condition, env))) {
                result = this.eval2(body, env)
            }
            return result;
        }

        // --------------------------------------------
        // Function calls:
        //
        // (print "Hello World")
        // (+ x 5)
        // (> foo bar)

        if (Array.isArray(exp)) {
            const fn = this.eval2(exp[0], env);

            const args = exp
                .slice(1)
                .map(arg => this.eval2(arg, env));

            // 1. Native function:

            // See Lecture 10

            if (typeof fn === 'function') {
                return fn(...args);
            }

            // 2. User-defined function:

            return this._callUserDefinedFunction(fn, args);
        }



        throw `Unimplemented: ${JSON.stringify(exp, types.getCircularReplacer())}`;
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

    _callUserDefinedFunction(fn, args) {
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


        return this._evalBody(fn.body, activationEnv);
    }

    _evalBody(body, env) {
        if (body[0] === 'begin') {
            return this._evalBlock(body, env);
        }
        return this.eval2(body, env);
    }

    _isNumber(exp) {
        return typeof exp === 'number';
    }

    _isString(exp) {
        return typeof exp === 'string' && exp[0] === '"' && exp.slice(-1) === '"';
    }

    _isVariableName(exp) {
        return typeof exp === 'string' && /^[+\-*/<>%=!a-zA-Z0-9_]+$/.test(exp);
    }

    _falsey(exp) {
        return !exp || (String(exp) === "0" && exp !== "0") || (exp instanceof Environment && exp.parent && exp.parent.record.hasOwnProperty("bool") &&
            this._callUserDefinedFunction(exp.parent.lookup("bool"), [exp]) === false);
    }

    evalFile(url, env = this.global) {

        try {
            const data = fs.readFileSync(path.join(__dirname, url), 'utf8')
            return this.eval(data);
        } catch (err) {
            console.error(err)
        }


    }
}




var GlobalEnvironment = new Environment({
    null: null,
    NaN: NaN,
    Infinity: Infinity,
    true: true,
    false: false,

    // Operators:

    '+'(op1, op2) {
        if (op1 instanceof Environment) {
            return new Skink()._callUserDefinedFunction(op1.parent.lookup("add"), [op1, op2]);
        }

        // if(typeof op1 === "string") {
        //     return  op1+String(op2);
        // }

        if (op1 instanceof types.Int || op1 instanceof types.Long) {
            return op1.add(op2);
        }

        if (typeof op1 === "string" || typeof op2 === "string") {
            return prettyPrint(op1) + prettyPrint(op2);
        }

        return parseDouble(op1) + parseDouble(op2);

    },

    '*'(op1, op2) {
        if (op1 instanceof Environment) {
            return new Skink()._callUserDefinedFunction(op1.parent.lookup("mul"), [op1, op2]);
        }


        if (op1 instanceof types.Int || op1 instanceof types.Long) {
            return op1.mul(op2);
        }

        return parseDouble(op1) * parseDouble(op2);
    },

    '-'(op1, op2 = null) {
        if (op1 instanceof Environment && op2 !== null) {
            return new Skink()._callUserDefinedFunction(op1.parent.lookup("sub"), [op1, op2]);
        }


        if (op2 == null) {
            if (op1 instanceof Environment) {
                return new Skink()._callUserDefinedFunction(op1.parent.lookup("neg"), [op1]);
            }

            if (op1 instanceof types.Int || op1 instanceof types.Long) {
                return op1.neg();
            }

            return -op1;
        }

        if (op1 instanceof types.Int || op1 instanceof types.Long) {
            return op1.sub(op2);
        }


        return parseDouble(op1) - parseDouble(op2);
    },

    '/'(op1, op2) {
        if (op1 instanceof Environment) {
            return new Skink()._callUserDefinedFunction(op1.parent.lookup("div"), [op1, op2]);
        }

        if (op1 instanceof types.Int || op1 instanceof types.Long) {
            return op1.div(op2);
        }

        return parseDouble(op1) / parseDouble(op2);
    },
    '%'(op1, op2) {
        if (op1 instanceof Environment) {
            return new Skink()._callUserDefinedFunction(op1.parent.lookup("mod"), [op1, op2]);
        }

        if (op1 instanceof types.Int || op1 instanceof types.Long) {
            return op1.mod(op2);
        }

        return parseDouble(op1) % parseFlaot(op2);
    },
    // Comparison:

    '>'(op1, op2) {
        if (op1 instanceof Environment) {
            return new Skink()._callUserDefinedFunction(op1.parent.lookup("gt"), [op1, op2]);
        }

        if (op1 instanceof types.Int || op1 instanceof types.Long) {
            return op1.compareTo(op2) > 0;
        }
        if (typeof op1 === "string" && typeof op2 === "string") {
            return op1.localeCompare(op2) > 0;
        }

        return parseDouble(op1) > parseDouble(op2);
    },

    '<'(op1, op2) {
        if (op1 instanceof Environment) {
            return new Skink()._callUserDefinedFunction(op1.parent.lookup("lt"), [op1, op2]);
        }


        if (op1 instanceof types.Int || op1 instanceof types.Long) {
            return op1.compareTo(op2) < 0;
        }

        if (typeof op1 === "string" && typeof op2 === "string") {
            return op1.localeCompare(op2) < 0;
        }

        return parseDouble(op1) < parseDouble(op2);
    },

    '>='(op1, op2) {
        var lt = GlobalEnvironment.lookup("<");
        return !lt(op1,op2);
    },

    '<='(op1, op2) {
        if (op1 instanceof Environment) {
            return new Skink()._callUserDefinedFunction(op1.parent.lookup("le"), [op1, op2]);
        }

        if (op1 instanceof types.Int || op1 instanceof types.Long) {
            return op1.compareTo(op2) <= 0;
        }

        if (typeof op1 === "string" && typeof op2 === "string") {
            return op1.localeCompare(op2) <= 0;
        }

        return parseDouble(op1) <= parseDouble(op2);
    },

    '='(op1, op2) {
        if (op1 instanceof Object || op2 instanceof Object) {
            return JSON.stringify(op1, types.getCircularReplacer()) === JSON.stringify(op2, types.getCircularReplacer());
        }

        return Object.is(op1, op2);
    },
    '!='(op1, op2) {
        return !(GlobalEnvironment.lookup("=")(op1, op2));
    },
    //Types
    'int'(op1) {
        if (isNaN(op1)) {
            op1 = String(op1).replace(/[^0-9]+?$/, "");
        }

        return new types.Int(op1);
    },
    'long'(op1) {
        if (isNaN(op1)) {
            op1 = String(op1).replace(/[^0-9]+?$/, "");
        }

        return new types.Long(op1);
    },
    "double": parseDouble,
    'string'(op1) {
        return prettyPrint(op1);
    },
    'boolean'(op1) {
        return !new Skink()._falsey(op1);
    },
    'type'(op1) {
        if (op1 instanceof Environment && op1.parent) {
            return op1.parent.__name__;
        }


        switch (getClass(op1)) {
            case "Null": return "null";
            case "Int": return "int";
            case "Long": return "long";
            case "Double": return "double";
            case "String": return "string";
            case "Boolean": return "boolean";
            default: return "other";
        }
    },
    'len'(op1) {
        return new types.Int(op1.length);
    },
    'substring'(op1, op2, op3 = String(op1).length) {
        return op1.substring(parseDouble(op2), parseDouble(op3));
    },
    'charAt'(op1, op2) {
        if (parseDouble(op2) < 0) {
            return op1.charAt(op1.length + parseDouble(op2));
        } else {
            return op1.charAt(parseDouble(op2));
        }
    },
    'ord'(op1) {
        return new types.Int(ord(prettyPrint(op1)))
    },
    // Console output:
    print(...args) {
        console.log(...args.map(prettyPrint));
    }
});

Function.prototype.toJSON = function () {
    return "[Function: " + this.name + "]";
}

//taken from https://stackoverflow.com/questions/13861254/json-stringify-deep-objects
// JSON.pruned : a function to stringify any object without overflow
// example : var json = JSON.pruned({a:'e', c:[1,2,{d:{e:42, f:'deep'}}]})
// two additional optional parameters :
//   - the maximal depth (default : 6)
//   - the maximal length of arrays (default : 50)
// GitHub : https://github.com/Canop/JSON.prune
// This is based on Douglas Crockford's code ( https://github.com/douglascrockford/JSON-js/blob/master/json2.js )


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
                return String(value);
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

function prettyPrint(a) {

    // if (Object.is(a, -0)) {
    //     return "-0.0";
    // }

    if (typeof a === "function") {
        return JSON.stringify(a).slice(1, -1);
    }


    if (Math.abs(a) === Infinity) {
        return a.toString();
    }

    if (a instanceof Environment && a.parent.has("toString")) {
        return prettyPrint(new Skink()._callUserDefinedFunction(a.parent.lookup("toString"), [a]));
    }

    if (String(a) === String({})) {
        return JSON.pruned(a,2);
    }

    if (typeof a === "number" && a === Math.floor(a) && !(a.toString().includes("e"))) {
        return a + ".0";
    }


    return String(a);
}



module.exports = Skink;