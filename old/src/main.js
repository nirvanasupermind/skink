var Skink = require("./Skink.js"), skink = new Skink();
// var fs = require("fs");
var util = require("util");
// var ArrayList = require("./ArrayList.js");



function prettyPrint(x) {
  let opts = { depth: null, colors: "auto" };
  let s = util.inspect(x, opts);
  return JSON.stringify(s);
}


// var myList = new ArrayList([1,2,3]);
// myList.add(1);
// prettyPrint(myList);
// skink.evalFile("./test.skink")
for(var i = 30; i < 40; i++) {
console.log(`${i} \u001b[0${i}m2\u001b[39m`);
}