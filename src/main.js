//Skink source code 
//Usage permitted under terms of MIT License

"use strict";
//Tests

var util = require("util");
var grammar = require("./grammar.js");
var rewrite = require("./rewrite.js");
var Interpreter = require("./Interpreter.js");
var type = require("./type.js");

//Driver code
function main() {
    var opts = { "depth": null, "colors": "auto" }
    var input = "test * 60";

    var [ast, error] = grammar.expr.parse(input);
    if (error) {
        console.log("ERROR:", error);
    } else {
        var sxp = rewrite(ast);
        var interpreter = new Interpreter();
        console.log(interpreter.eval(sxp).value.toString());
    }
}

main();