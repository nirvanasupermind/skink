var chevrotain = require("chevrotain")
var tokens = require("./tokens.js")
console.log(tokens.lexer.tokenize("int a = 2;"))