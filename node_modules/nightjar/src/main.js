//nightjar Library
//Usage permitted under terms of MIT License

//testing file
var nightjar = require("./nightjar.js");
function get_performance(task) {
    var a = Date.now();
    task();
    var b = Date.now();
    return b-a;
}
function main() {
   var a = nightjar.random.random([2]);
   console.log(a.toString());
}

main();
