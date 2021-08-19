var Lexer = require("./Lexer.js");
var Parser = require("./Parser.js");

var input = " -1 + 2 * 3 foo";

var tokens = new Lexer(input).lex();

var ast = new Parser(tokens).parse();
console.log(ast);