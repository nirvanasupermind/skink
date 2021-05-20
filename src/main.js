var Int32 = require("./Int32.js");
var Int64 = require("./Int64.js");
function perf(task) {
    console.time();
    task();
    console.timeEnd();
}

console.log(new Int64(20));