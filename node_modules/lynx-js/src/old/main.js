var w = require("./wombat.js")
function forwardPath(x, m, b) {
    return m * x + b;
}

console.log(w.curve_fit(forwardPath,[1,2,3],[2,4,6]))