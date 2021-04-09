var P = require("parsimmon");
var wrappers = require("./wrappers.js");
var Environment = require("./Environment.js");
var E = () => new Environment({});
// var INVALID = "int a=;";

// Use the JSON standard's definition of whitespace rather than Parsimmon's.
let whitespace = P.regexp(/\s*/m);

// JSON is pretty relaxed about whitespace, so let's make it easy to ignore
// after most text.
function token(parser) {
    return parser.wrap(whitespace, whitespace);
}


// Turn escaped characters into real ones (e.g. "\\n" becomes "\n").
function interpretEscapes(str) {
    let escapes = {
        b: "\b",
        f: "\f",
        n: "\n",
        r: "\r",
        t: "\t"
    };
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

function alt() {
  var parsers = [].slice.call(arguments);
  var numParsers = parsers.length;
  return P(function(input, i) {
    console.log(input,i);
    var result;
    for (var j = 0; j < parsers.length; j += 1) {
      result = parsers[j].parse(input);
      if (result.status) {
        return result;
      }
    }
    return result;
  });
}

// Several parsers are just strings with optional whitespace.
function word(str) {
    return token(P.string(str));
}

/**
 * Skink parser.
 */
var Lang = P.createLanguage({
    /////////////////////////////////////
    //LITERALS
    // Regexp based parsers should generally be named for better error reporting.
    int() {
        return token(P.regexp(/\b\d+\b/))
            .map((results) => wrappers.int.record.constructor(E(), results))
            .desc("int-literal");
    },
    long() {
        return token(P.regexp(/\b\d+L\b/))
            .map((results) => wrappers.int.record.constructor(E(), results.slice(0, -1)))
            .desc("long-literal");
    },
    double() {
        return token(P.regexp(/(\d+)?\.(\d+)|\b[0-9]+(\.[0-9]+)?(e[+-]?[0-9]+)\b/))
            .map((results) => wrappers.double.record.constructor(E(), results))
            .desc("double-literal");
    },
    string() {
        return token(P.regexp(/"[^"\\\r\n]*(?:\\.[^"\\\r\n]*)*"/))
            .map((results) => wrappers.string.record.constructor(E(), interpretEscapes(results.slice(1, -1))))
            .desc("string-literal");
    },
    literal(r) {
        return P.alt(
            r.string,
            r.double,
            r.long,
            r.int
        )
    },
    /////////////////////////////////////
    //IDENTIFIERS AND TEXT
    lbrace() {
        return word("(");
    },
    rbrace() {
        return word(")");
    },
    lineBreak(r) {
        return P.oneOf(";\r\n").many();
    },
    identifier() {
        return P.regexp(/[_a-zA-Z\$][_a-zA-Z0-9\$]*/).desc("identifier");
    },
    /////////////////////////////////////
    //EXPRESSIONS
    group(r) {
        return r.expr.wrap(r.lbrace, r.rbrace);
    },
    wsGroup(r) {
        return P.seq(P.string("("), whitespace, r.expr, whitespace, P.string(")"), P.whitespace)
            .map((results) => results[2]);
    },
    semigroup(r) {
        return P.alt(r.identifier, r.group);
    },
    wsSemigroup(r) {
        return P.alt(r.identifier.skip(P.whitespace), r.wsGroup);
    },
    arg(r) {
        return P.seq(
            r.wsSemigroup,
            r.identifier
        )
    },
    varExpr(r) {
        return P.seq(r.arg, word("="), r.expr).map((results) => {
            var [a, b] = [results[0], results[2]];
            return ["var", a[1], ["_typeAssert", b, a[0]]];
        });
    },
    setExpr(r) {
        return P.seq(r.identifier.skip(word("=")), r.expr)
            .map((results) => ["set"].concat(results));
    },
    block(r) {
        return r.file.wrap(word("{"), word("}"));
    },
    body(r) {
        return r.block;
    },
    funcExpr(r) {
        return P.seq(
            r.arg,
            r.lbrace,
            r.arg.sepBy(word(",")),
            r.rbrace,
            r.body
        ).map((results) => {
            var [a, b, c] = [results[0], results[2], results[4]];
            return ["var", a[1], ["lambda", b.map((e) => e[1]), ["begin",
                ["return", ["_typeAssert", c, a[0]]]
            ]]]
        })
    },
    lambdaExpr(r) {
        return P.seq(
            r.lbrace,
            r.arg.sepBy(word(",")),
            r.rbrace,
            word("->"),
            r.identifier,
            P.whitespace,
            r.body
        ).map((results) => {
            var [a, b, c] = [results[1], results[4], results[6]];
            return ["lambda", a.map((e) => e[1]), ["begin", ["return", ["_typeAssert", c, b]]]];
        });
    },
    dotExpr(r) {
        return P.seq(r.semigroup, word(".").then(r.identifier).many()).map((results) => {
            var result = ["prop", results[0], wrappers.string.record.constructor(E(), results[1][0])];
            for (var i = 1; i < results[1].length; i++) {
                result = ["prop", result, wrappers.string.record.constructor(E(), results[1][i])];
            }

            return result;
        });
    },
    keyExpr(r) {
        return P.seq(r.semigroup, r.expr.wrap(word("["), word("]")).many()).map((results) => {
            var result = ["prop", results[0], results[1][0]];
            for (var i = 1; i < results[1].length; i++) {
                result = ["prop", result, results[1][i]];
            }

            return result;
        });
    },
    propExpr(r) {
        return alt(r.dotExpr,r.keyExpr);
    },
    funcCall(r) {
        return P.seq(
            r.semigroup,
            r.expr.sepBy(word(",")).wrap(r.lbrace, r.rbrace)
        ).map((results) => [results[0]].concat(results[1]));
    },
    returnExpr(r) {
        return P.seq(P.string("return").skip(P.whitespace), r.expr);
    },
    classExpr(r) {
        return P.seq(
            word("class"),
            r.identifier,
            r.block
        ).map((results) => {
            var [name, body] = results.slice(1);
            var cons = body.filter((e) => e && e[0] === "var" && e[1] === "constructor")[0];
            if (cons === undefined) {
                return ["class", name, null, ["begin",
                    ["var", "constructor", ["lambda", ["this"], ["begin",
                        ["namespace", "_", body],
                        ["_assign", "this", "_"]
                    ]]]
                ]];
            } else {
                return ["class", name, null, ["begin",
                    ["var", "constructor", ["lambda", ["this"].concat(cons[2][1]), ["begin",
                        ["namespace", "_", body.filter((e) => !(e && e[0] === "var" && e[1] === "constructor"))],
                        ["_assign", "this", "_"]
                    ]]]
                ]]
            }
        })
    },
    expr(r) {
        return P.alt(
            r.classExpr,
            r.funcExpr,
            r.lambdaExpr,
            r.funcCall,
            r.block,
            r.returnExpr,
            r.setExpr,
            r.varExpr,
            r.literal,
            r.group,
            r.dotExpr,
            r.identifier
        )
    },
    // This is the main entry point of the parser: a full Skink file.
    file(r) {
        return r.expr.trim(r.lineBreak).many().map((results) => ["begin"].concat(results));
    }
});
module.exports = Lang;
// //Skink parser.
// module.exports = new function () {
//     /////////////////////////////////////
//     //LITERALS
//     var r = this;
//     this.int = function () {
//         return token(P.regexp(/\b\d+\b/))
//             .map((results) => wrappers.int.record.constructor(E(), results))
//             .desc("int-literal");
//     }

//     this.long = function () {
//         return token(P.regexp(/\b\d+\b/))
//             .map((results) => wrappers.int.record.constructor(E(), results))
//             .desc("long-literal");
//     }

//     this.double = function () {
//         return token(P.regexp(/(\d+)?\.(\d+)|\b[0-9]+(\.[0-9]+)?(e[+-]?[0-9]+)\b/))
//             .map((results) => wrappers.double.record.constructor(E(), results))
//             .desc("double-literal");
//     }

//     this.literal = function () {
//         return P.alt(
//             r.double(),
//             r.long(),
//             r.int()
//         )
//     }

//     /////////////////////////////////////
//     //IDENTIFIERS

//     /////////////////////////////////////
//     //EXPRESSIONS
//     this.expr = P.alt(
//         r.literal(),
//         r.expr
//     )
// }