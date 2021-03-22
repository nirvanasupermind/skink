// lynx Library
// Copyright (c) nirvanasupermind
// Usage permitted under terms of MIT License

var lynx = require("./lynx.js");
var tensorMethods = ["size",
    "zeros",
    "ones",
    "full",
    "sqrtm",
    "arange"];
var method = "sqrtm"

console.log(JSON.stringify(Object.getOwnPropertyNames(lynx).sort()));
var x0 = new lynx.NdArray([39,35,22,23])
var x1 = -1
console.log(lynx.polyval(x0,x1)) /*NaN*/
console.log("=================")

//=================
function root(f) {
    function fDash(x) {
        var h = 1.5e-8;
        return (f(x.add(h)).sub(f(x.sub(h)))).div(2 * h);
    }



    var result = new lynx.Dual(1);
    for (var i = 0; i < 75; i++) {
        result = result.sub(f(result).div(fDash(result)));
    }

    return result;
}
//=================
function rng() { return flipAnotherCoin() ? Math.floor(Math.random() * len * 2) / 2 - len :  Math.floor(Math.random() * len * 2)};
var len = +new Date() % 30;
var len2 = +new Date() % 6;

var flipACoin = +new Date() % 5;
var flipAnotherCoin = () => +new Date() % 2;
function rand() {
    if(tensorMethods.includes(method)) {
        return new lynx.NdArray([new Array(len2).join("a").split("a").map(rng), new Array(len2).join("a").split("a").map(rng)]);
    }

    switch(flipACoin) {
        case 0: return new lynx.NdArray(new Array(len2).join("a").split("a").map(rng));
        case 1: return new lynx.Dual(rng(),rng());
        // case 2: return new lynx.NdArray([new Array(len2).join("a").split("a").map(rng), new Array(len2).join("a").split("a").map(rng)]);
        default: return new lynx.NdArray(new Array(len2).join("a").split("a").map(rng));
    }
}



function ndCall(n) {
    if(typeof n === "number")
        return n+"";
    if(n.tolist)
        return "new lynx.NdArray("+JSON.stringify(n.tolist())+")";
    return "new lynx.Dual(" + [n.a,n.b] + ")";
}

function getExample(theMethod) {
    var examples = [];
    for (var i = 0; i < lynx[theMethod].length; i++) {
        examples.push(rand());
    }

    var code = [];
    var args = [];
    for (var i = 0; i < examples.length; i++) {
        args.push("x" + i);
        code.push(["var x", i, " = ", ndCall(examples[i])].join(""));
    }

    eval(code.join("\n"));
    var t1 = `console.log(lynx.${theMethod}(${args}))`;
    code.push(t1 + " /*"+eval(t1.split("(").slice(1).join("(").split(")")[0]+")")+"*/");
    return code.join("\n");
}


var x0 = new lynx.NdArray([[0.5,1.5,2],
    [0.5,2.5,1]]);
console.log(getExample(method));