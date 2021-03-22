/*
  In this module, we create a Skink parser using parsimmon.
  It will output an S-expression that can be interpreted.
*/
var P = require("parsimmon");
var types = require("./types.js");
var Skink = require("./Skink.js");
let construct = (a, b) => new Skink().eval2(["new", a, ...b]);


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
        return P.regexp(/[-+]?\b\d+\b/).map((e) => construct(types.Int, [Skink.Int(e)]))
            .desc("IntegerLiteral");
    },
    long(r) {
        //in parsimmon, "r" refers to the parent object
        return P.regexp(/[-+]?\b\d+L\b/)
            .map((e) => construct(types.Long, [Skink.Long(e.slice(0, -1))]))
            .desc("LongLiteral");
    },
    double(r) {
        return P.regexp(/[+-]?\b(?=\d*[.eE])(?=\.?\d)\d*\.?\d*(?:[eE][+-]?\d+)?\b/).map((e) => construct(types.Double, [Number.parseFloat(e)]))
            .desc("FloatingPointLiteral");
    },
    identifier() {
        return P.regexp(/[_a-zA-Z][_a-zA-Z0-9]*/)
            .desc("Identifier")
    },
    literal(r) {
        return P.alt(
            r.double,
            r.int,
            r.long
        );
    },
    //EXPRESSIONS
    varExpr(r) {
        return P.seqMap(
            r.identifier,
            P.whitespace,
            r.identifier,
            _,
            P.string("="),
            _,
            r.expr,
            (a, _1, b, _2, _3, _4, c) => {
                return ["var",b,["__typeAssert",c,a]];
            });
    },
    //OTHER
    expr(r) {
        return P.alt(r.varExpr, r.identifier, r.literal);
    },
    code(r) {
        return r.expr;
    }
});

//Parsing function.
function parse(x) {
    return Lang.code.tryParse(x);
}

//Export.
module.exports = { Lang, parse }