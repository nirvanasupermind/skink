/*
  In this module, we create a Skink parser using parsimmon.
  It will output an S-expression that can be interpreted.
*/
var P = require("parsimmon");
var types = require("./types.js");
// var types = require("./types.js");
// var Skink = require("./Skink.js");
var Environment = require("./Environment.js");
// let construct = (a, b) => new Skink().eval2(["new", a, ...b]);
var lynx = require("lynx-js");

// Use the JSON standard's definition of whitespace rather than Parsimmon's.
let _ = P.regexp(/\s*/m);
// JSON is pretty relaxed about whitespace, so let's make it easy to ignore
// after most text.
function token(parser) {
    return parser.skip(_);
}

// Several parsers are just strings with optional whitespace.
function word(str) {
    return P.string(str).thru(token);
}


var Lang = P.createLanguage({ //create a language    
    //LITERALS
    int() {
        //Do not forget the word boundaries!
        return P.regexp(/[-+]?\b\d+\b/)
            .map(types.Int)
            .desc("IntLiteral");
    },
    long() {
        //Do not forget the word boundaries!
        return P.regexp(/[-+]?\b\d+L\b/)
            .map((results) => types.Long(results.slice(0,-1)))
            .desc("LongLiteral");
    },
    double(r) {
        return P.regexp(/[+-]?\b(?=\d*[.eE])(?=\.?\d)\d*\.?\d*(?:[eE][+-]?\d+)?\b/)
            .map(Number.parseFloat)
            .desc("FloatingPointLiteral");
    },
    identifier() {
        return P.regexp(/[_a-zA-Z][_a-zA-Z0-9]*/)
            .desc("Identifier")
    },
    literal(r) {
        return P.alt(
            r.double,
            r.long,
            r.int
        );
    },
    //EXPRESSIONS
    varExpr(r) {
        return P.seqMap(
            P.string("var"),
            P.whitespace,
            r.identifier,
            _,
            P.string("="),
            _,
            r.expr,
            (a, _2, b, _3, _4, _5, c) => {
                return ["var", b, c];
            });
    },
    setExpr(r) {
        return P.seqMap(
            r.identifier,
            _,
            P.string("="),
            _,
            r.expr,
            (a, _1, _2, _3, b) => {
                return ["set", a, b[0]];
            }
        )

        //Input: a=2
        //WE DO NOT WANT THIS RESULT: ["set","a",2]
        //BUT THIS INSTEAD: ["set","a",["__typeAssert",2,"int"]]
        //but we need to access type of 2
    },
    group(r) {
        return P.seq(P.string("("), r.expr, P.string(")")).map((results) => results[1][0]);
    },
    block(r) {
        return P.seq(P.string("{"), r.code, P.string("}")).map((results) => results[1]);
    },
    expr(r) {
        return P.alt(
            r.varExpr,
            r.setExpr,
            r.group,
            r.block,
            r.identifier,
            r.literal,
            P.string("")
        );
    },
    lineBreak() {
        return P.oneOf("\n;").desc("LineBreak")
    },
    code(r) {
        return r.expr
            .trim(P.optWhitespace)
            .sepBy(r.lineBreak)
            .map((e) => ["begin", ...e]);
    }
});

//Parsing function.
function parse(x) {
    return Lang.code.tryParse(x);
}

//Export.
module.exports = { Lang, parse }