var Int32 = require("./GenericInt.js")(32);
var Environment = require("./Environment.js");
var wrappers = require("./wrappers.js");
var util = require("util");
var Lang = require("./parser.js");
var P = require("parsimmon");

function prettyPrint(x) {
    let opts = { depth: null, colors: "auto" };
    let s = util.inspect(x, opts);
    console.log(s);
}

//Driver code
function main() {
prettyPrint(Lang.dotExpr.parse(`this["x"]`,0));
}

main();