var lynx = require("lynx-js");
var parser = require("./parser.js");
var Skink = require("./Skink.js"), skink = new Skink();
var Environment = require("./Environment.js");
var types = require("./types.js");
console.log(skink.eval2(parser.parse("var x = 2.0;")));

//object-oriented language
//everything is an object
//strongly-typed(?), interpreted
//out-of-box math package