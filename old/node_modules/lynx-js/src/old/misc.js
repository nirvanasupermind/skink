//This file contains stuff that isn't assosciated to any class
var Dual = require("./dual.js");
var sqrtpi = Math.sqrt(Math.PI);
var eulerGamma = 0.5772156649015328606065120;
var learningFactor = 0.5;

/**
 * Find the integral of a function at a point
 * using the composite trapezoidal rule.
 * @param {function} f  
 * @param {number} a
 * @param {number} b 
 * @param {number} [n] 
 */
function integral(f, a, b, n = 5000) {
    var t1 = (b - a) / n;
    var t2 = f(a) / 2;
    for (var k = 1; k < n; k++) {
        var s1 = a;
        var s2 = (k * (b - a)) / n;
        t2 += f(s1 + s2);
    }

    t2 += f(b) / 2;
    return t1 * t2;

}

/**
 * Computes the factorial of n, using gamma function
 * @param {number} n 
 */
function fac(n) {
    if (n >= 0 && n <= 19 && n === Math.floor(n)) {
        // Return some "Preset" values for nonnegative integers
        switch (n) {
            case 0: return 1;
            case 1: return 1;
            case 2: return 2;
            case 3: return 6;
            case 4: return 24;
            case 5: return 120;
            case 6: return 720;
            case 7: return 5040;
            case 8: return 40320;
            case 9: return 362880;
            case 10: return 3628800;
            case 11: return 39916800;
            case 12: return 479001600;
            case 13: return 6227020800;
            case 14: return 87178291200;
            case 15: return 1307674368000;
            case 16: return 20922789888000;
            case 17: return 355687428096000;
            case 18: return 6402373705728000;
            case 19: return 121645100408832000;
        }

    } else if (n < 0) { //Negative number: Use Weierstrass's product
        var z = n + 1;
        var result = Math.exp(-(eulerGamma * z)) / z;
        for (var n2 = 1; n2 < 1000; n2++) {
            result *= Math.pow(1 + (z / n2), -1) * Math.exp(z / n2);
        }

        return result;
    } else {
        //This is our main body: The number is a non-integer >= 0
        //Use optimized Ramanujan approximation
        var t1 = Math.sqrt(Math.PI);
        var t2 = Math.pow(n / Math.E, n);
        var t3 = 8 * n * n * n + 4 * n * n + n + 1 / (Math.PI * Math.PI * Math.PI);
        return t1 * t2 * Math.pow(t3, 1 / 6);
    }

}

var STRIP_COMMENTS = /((\/\/.*$)|(\/\*[\s\S]*?\*\/))/mg;
var ARGUMENT_NAMES = /([^\s,]+)/g;

function getParamNames(func) {
    var fnStr = func.toString().replace(STRIP_COMMENTS, '');
    var result = fnStr.slice(fnStr.indexOf('(') + 1, fnStr.indexOf(')')).match(ARGUMENT_NAMES);
    if (result === null)
        result = [];
    return result;
}

//from https://stackoverflow.com/questions/25582882/javascript-math-random-normal-distribution-gaussian-bell-curve
function gaussianRand() {
    var rand = 0;

    for (var i = 0; i < 6; i += 1) {
        rand += Math.random();
    }

    return rand / 6;
}

function gaussianRandom(start, end) {
    return Math.floor(start + gaussianRand() * (end - start + 1));
}

/**
 * Computes the arithmetic mean.
 * @param {number[]} data 
 */
function mean(data) {
    return data.reduce((acc, no) => acc + no) / data.length;
}

//Util function to add the delta
function add(a, b) {
    return a.map((e) => e + b);
}

function cost(f, xData, yData) {
    var result = 0;
    var m = xData.length;
    for (var i = 0; i < m; i++) {
        var yHat = f(xData[i]);
        result += Math.pow(yHat - yData[i], 2);
    }

    result /= m;
    return result;
}


function costPartial(f, xData, yData) {
    var result = 0;
    var m = xData.length;
    for (var i = 0; i < m; i++) {
        var yHat = f(xData[i]);
        result += (yHat - yData[i])**2;
    }

    result /= m;
    return result;
}



function numericalDeriv(f, x) {
    var h = Math.sqrt(Number.EPSILON);
    return (f(x + h) - f(x - h)) / (2 * h);
}

function numericalPartialDeriv(f, x, v) {
    var idx = getParamNames(f).indexOf(v);
    function g(n) {
        var x2 = x;
        x2[idx] = n;
        return f(...x2);
    }


    return numericalDeriv(g, x[idx], 1);
}

/**
 * Performs regression for a set of data points using the supplied model.
 * @param {function} f 
 * @param {number[]} xData 
 * @param {number[]} yData
 */
function curve_fit(f, xData, yData) {
    var numParams = f.length - 1;
    var theta = [];

    for (var i = 0; i < numParams; i++) {
        theta.push(1); //Random init
    }

    for(var i = 0; i < 1; i++) {
        var delta = costPartial((e) => f(e,...theta),xData,yData)
        console.log({delta})
        theta = theta.map((e) => e-delta);
    }

    



    return theta;
}


module.exports = { integral, fac, mean, curve_fit, numericalPartialDeriv }