var Skink = require("./Skink.js"), skink = new Skink();
// var fs = require("fs");
// var util = require("util");
// var ArrayList = require("./ArrayList.js");

// function prettyPrint(x) {
//   let opts = { depth: null, colors: "auto" };
//   let s = util.inspect(x, opts);
//   console.log(s);
//   return s;
// }

// var myList = new ArrayList([1,2,3]);
// myList.add(1);
// prettyPrint(myList);
skink.evalFile("./test.skink")