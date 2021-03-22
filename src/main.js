var types = require("./types.js");
var lynx = require("lynx-js");
var parser = require("./parser.js");
var Skink = require("./Skink.js"), skink = new Skink();
var Environment = require("./Environment.js");

console.log(skink.eval2(["__typeAssert",8,"int"]));