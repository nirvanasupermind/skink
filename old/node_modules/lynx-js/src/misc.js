// lynx Library
// Copyright (c) nirvanasupermind
// Usage permitted under terms of MIT License


var NdArray = require("./NdArray.js");
var Dual = require("./Dual.js");
var Int = require("./Int.js");
// var float = require("./float.js")
// var Complex = require("./Complex.js")
var assert = require("assert")
var type = NdArray._.type;
var applyScalar = NdArray._.applyScalar;

//from https://stackoverflow.com/questions/1458633/how-to-deal-with-floating-point-number-precision-in-javascript
var _cf = (function () {
    function _shift(x) {
        var parts = x.toString().split('.');
        return (parts.length < 2) ? 1 : Math.pow(10, parts[1].length);
    }
    return function () {
        return Array.prototype.reduce.call(arguments, function (prev, next) { return prev === undefined || next === undefined ? undefined : Math.max(prev, _shift(next)); }, -Infinity);
    };
})();

Math.a = function () {
    var f = _cf.apply(null, arguments); if (f === undefined) return undefined;
    function cb(x, y, i, o) { return x + f * y; }
    return Array.prototype.reduce.call(arguments, cb, 0) / f;
};

Math.s = function (l, r) { var f = _cf(l, r); return (l * f - r * f) / f; };

Math.m = function () {
    var f = _cf.apply(null, arguments);
    function cb(x, y, i, o) { return (x * f) * (y * f) / (f * f); }
    return Array.prototype.reduce.call(arguments, cb, 1);
};

Math.d = function (l, r) { var f = _cf(l, r); return (l * f) / (r * f); };

/**
 * Returns the number of elements in an NdArray along a given axis.
 * @param {*} x 
 * @param {number} y 
 */
function size(x, y) {
    x = x.value;
    for (var i = 0; i < y; i++) {
        x = x[0];
    }
    return x.length;
}

/**
 * Return a new NdArray of given shape, filled with zeros. 
 * @param {number|number[]} x 
 */
function zeros(x) {
    if (x.length === 1 || typeof x === "number") {
        x = NdArray._.list(x)
        return new NdArray(JSON.parse("[" + "0,".repeat(x[0] - 1) + "0" + "]"));
    }

    var result = JSON.parse(JSON.stringify(new Array(x[0]))).map(() => zeros(x.slice(1)).value);
    return new NdArray(result);
}
/**
 * Return a new NdArray of given shape, filled with ones. 
 * @param {number|number[]} x 
 */
function ones(x) {
    if (x.length === 1 || typeof x === "number") {
        x = NdArray._.list(x)
        return new NdArray(JSON.parse("[" + "1,".repeat(x[0] - 1) + "1" + "]"));
    }

    var result = JSON.parse(JSON.stringify(new Array(x[0]))).map(() => ones(x.slice(1)).value);
    return new NdArray(result);
}

/**
 * Return a new NdArray of given shape, filled with fill_value.
 * @param {number|number[]} x 
 * @param {number|number[]} fill_value 
 */
function full(x, fill_value) {
    fill_value = type(fill_value) === "Number" ? fill_value : NdArray._.list(fill_value)
    if (x.length === 1 || type(x) === "Number") {
        x = NdArray._.list(x)
        return new NdArray(JSON.parse("[" + `${JSON.stringify(fill_value)},`.repeat(x[0] - 1) + JSON.stringify(fill_value) + "]"));
    }

    var result = JSON.parse(JSON.stringify(new Array(x[0]))).map(() => full(x.slice(1), fill_value).value);
    return new NdArray(result);
}



/**
 * Returns an array of evenly spaced values within a given interval.
 * @param {number} x 
 * @param {number} y 
 * @param {number} [z]
 */
function arange(x, y, z = 1) {
    z = NdArray._.list(z);
    var result = new NdArray([]);
    var j = 0;
    for (var i = x; i < y; i = Math.a(i, z[j % z.length])) {
        j++;
        result.set(j, i);
    }

    return result;
}

/**
 * Return the identity array. The identity array is a square array with ones on the main diagonal.
 * @param {number} x 
 */
function identity(x) {
    x = parseFloat(x);
    var result = [];
    for (var i = 0; i < x; i++) {
        result.push([])
        for (var j = 0; j < x; j++) {
            if (i === j) {
                result[i].push(1);
            } else {
                result[i].push(0);
            }
        }
    }

    return new NdArray(result);
}
/**
 * Computes sine. If the input is an array, the function will be performed element-wise.
 * @param {*} x 
 */
function sin(x) {
    if (type(x) === "Dual") { //dual number
        return new Dual(Math.sin(x.a), x.b * Math.cos(x.a));
    } else if (type(x) === "NdArray" || type(x) === "Array") { //array
        x = new NdArray(x);
        return new NdArray(applyScalar(Math.sin, x.value));
    } else { //number
        x = parseFloat(x);
        return Math.sin(x);
    }
}

/**
 * Computes cosine. If the input is an array, the function will be performed element-wise.
 * @param {*} x 
 */
function cos(x) {
    if (type(x) === "Dual") { //dual number
        return new Dual(Math.cos(x.a), -x.b * Math.sin(x.a));
    } else if (type(x) === "NdArray" || type(x) === "Array") { //array
        x = new NdArray(x);
        return new NdArray(applyScalar(Math.cos, x.value));
    } else { //number
        x = parseFloat(x);
        return Math.cos(x);
    }
}


/**
 * Computes tangent. If the input is an array, the function will be performed element-wise.
 * @param {*} x 
 */
function tan(x) {
    if (type(x) === "Dual") { //dual number
        return new Dual(Math.tan(x.a), x.b * 1 / (Math.cos(x.a) * Math.cos(x.a)));
    } else if (type(x) === "NdArray" || type(x) === "Array") { //array
        x = new NdArray(x);
        return new NdArray(applyScalar(Math.tan, x.value));
    } else { //number
        x = parseFloat(x);
        return Math.tan(x);
    }
}


/**
 * Inverse sine. If the input is an array, the function will be performed element-wise.
 * @param {*} x 
 */
function asin(x) {
    if (type(x) === "Dual") { //dual number
        var t1 = 1 / Math.sqrt(1 - (x.a * x.a));
        return new Dual(Math.asin(x.a), x.b * t1);

        if (x.b === 0 && isFinite(asin(x.a)))
            return new Complex(asin(x.a));
        var _i = new Complex(0, 1);
        var t1 = _i.mul(x).add(new Complex(1).sub(x.pow(2)).pow(0.5));
        return new Complex(Math.atan2(t1.b, t1.a), -Complex._.ln(t1).a);
    } else if (type(x) === "NdArray" || type(x) == "Array") { //array
        x = new NdArray(x);
        return new NdArray(applyScalar(Math.asin, x.value));
    } else { //number
        x = parseFloat(x);
        return Math.asin(x);
    }
}


/**
 * Inverse cosine. If the input is an array, the function will be performed element-wise.
 * @param {*} x 
 */
function acos(x) {
    if (type(x) === "Dual") { //dual number
        var t1 = -1 / Math.sqrt(1 - (x.a * x.a));
        return new Dual(Math.asin(x.a), x.b * t1);

        function f(x2) {
            return cos(x2).sub(x);
        }

        function fDash(x2) {
            return sin(x2).mul(-1);
        }


        var result = new Complex(1);
        for (var i = 0; i < 75; i++) {
            result = result.sub(f(result).div(fDash(result)));
        }

        return result;
    } else if (type(x) === "NdArray" || type(x) === "Array") { //array
        x = new NdArray(x);
        return new NdArray(applyScalar(Math.acos, x.value));
    } else { //number
        x = parseFloat(x);
        return Math.acos(x);
    }
}

/**
 * Inverse tangent. If the input is an array, the function will be performed element-wise.
 * @param {*} x 
 */
function atan(x) {
    if (type(x) === "Dual") { //dual number
        var t1 = 1 / (1 + (x.a * x.a));
        return new Dual(Math.asin(x.a), x.b * t1);
    } else if (type(x) === "NdArray" || type(x) === "Array") { //array
        x = new NdArray(x);
        return new NdArray(applyScalar(Math.atan, x.value));
    } else { //number
        x = parseFloat(x);
        return Math.acos(x);
    }
}


/**
 * Exponential function. If the input is an array, the function will be performed element-wise.
 * @param {*} x 
 */
function exp(x) {

    if (type(x) === "Dual") { //dual number
        return Dual._.exp(x);
    } else if (type(x) === "NdArray" || type(x) === "Array") { //array
        x = new NdArray(x);
        return new NdArray(applyScalar(Math.exp, x.value));
    } else { //number
        x = parseFloat(x);
        return Math.exp(x);
    }
}



/**
 * Returns the natural logarithm. If the input is an array, the function will be performed element-wise.
 * @param {*} x 
 */
function log(x) {
    if (type(x) === "Dual") { //dual number
        return new Dual(Math.log(Math.abs(x.a)), x.ab / x.a);
    } else if (type(x) === "NdArray" || type(x) == "Array") { //array
        x = new NdArray(x);
        return new NdArray(applyScalar(log, x.value));
    } else { //number
        x = parseFloat(x);
        return Math.log(Math.abs(x));
    }
}

// var logarithm = log;

function _sqrt(n) {
    return (n > 0) ? Math.sqrt(n) : 0;
}

/**
 * Returns the square root. If the input is an array, the function will be performed element-wise.
 * @param {*} x 
 */
function sqrt(x) {
    if (type(x) === "Dual") { //dual number
        var t1 = 1 / (2 * _sqrt(x.a));
        return new Dual(_sqrt(x.a), x.b * t1);
    } else if (type(x) === "NdArray" || type(x) == "Array") { //array
        x = new NdArray(x);
        return new NdArray(applyScalar(_sqrt, x.value));
    } else { //number
        x = parseFloat(x);
        return _sqrt(x);
    }
}

/**
 * Returns the cube root. If the input is an array, the function will be performed element-wise.
 * @param {*} x 
 */
function cbrt(x) {
    if (type(x) === "Dual") { //dual number
        var t1 = 1 / (3 * Math.cbrt(x.a * x.a));
        return new Dual(Math.cbrt(x.a), x.b * t1);
    } else if (type(x) === "NdArray" || type(x) == "Array") { //array
        x = new NdArray(x);
        return new NdArray(applyScalar(Math.cbrt, x.value));
    } else { //number
        x = parseFloat(x);
        return Math.cbrt(x);
    }
}


/**
 * Returns ceil of number. If the input is an array, the function will be performed element-wise.
 * @param {*} x 
 */
function ceil(x) {
    if (type(x) === "Dual") { //dual number
        // var t1 = 1 / (3 * Math.cbrt(x.a * x.a));
        return new Dual(Math.ceil(x.a), 0);
    } else if (type(x) === "NdArray" || type(x) == "Array") { //array
        x = new NdArray(x);
        return new NdArray(applyScalar(Math.ceil, x.value));
    } else { //number
        x = parseFloat(x);
        return Math.ceil(x);
    }
}


/**
 * Returns floor of number. If the input is an array, the function will be performed element-wise.
 * @param {*} x 
 */
function floor(x) {
    if (type(x) === "Dual") { //dual number
        // var t1 = 1 / (3 * Math.cbrt(x.a * x.a));
        return new Dual(Math.floor(x.a), 0);
    } else if (type(x) === "NdArray" || type(x) == "Array") { //array
        x = new NdArray(x);
        return new NdArray(applyScalar(Math.floor, x.value));
    } else { //number
        x = parseFloat(x);
        return Math.floor(x);
    }
}



/**
 * Returns the rounded number. If the input is an array, the function will be performed element-wise.
 * @param {*} x 
 */
function round(x) {
    if (type(x) === "Dual") { //dual number
        // var t1 = 1 / (3 * Math.cbrt(x.a * x.a));
        return new Dual(Math.round(x.a), 0);
    } else if (type(x) === "NdArray" || type(x) == "Array") { //array
        x = new NdArray(x);
        return new NdArray(applyScalar(Math.round, x.value));
    } else { //number
        x = parseFloat(x);
        return Math.round(x);
    }
}


/**
 * Use composite trapezoidal rule with "n" subintervals to compute integral.
 * @param {function} f 
 * @param {number} a
 * @param {number} b
 * @param {number} [n] 
 */
function integral(f, a, b, n = 5000) {
    var t1 = (b - a) / n;
    var t2 = f(a) / 2;
    for (var k = 1; k <= n - 1; k++) {
        var u1 = k * t1;
        t2 += f(a + u1);
    }
    t2 += f(b) / 2;
    return t1 * t2;
}



//taken from https://github.com/Naruyoko/OmegaNum.js/blob/master/OmegaNum.js
//All of these are from Patashu's break_eternity.js
var OMEGA = 0.56714329040978387299997;  //W(1,0)
//from https://math.stackexchange.com/a/465183
//The evaluation can become inaccurate very close to the branch point
function f_lambertw(z, tol) {
    if (tol === undefined) tol = 1e-10;
    var w;
    var wn;
    if (!Number.isFinite(z)) return z;
    if (z === 0) return z;
    if (z === 1) return OMEGA;
    if (z < 10) w = 0;
    else w = Math.log(z) - Math.log(Math.log(z));
    for (var i = 0; i < 100; ++i) {
        wn = (z * Math.exp(-w) + w * w) / (w + 1);
        if (Math.abs(wn - w) < tol * Math.abs(wn)) return wn;
        w = wn;
    }
    throw Error("Iteration failed to converge: " + z);
    //return Number.NaN;
};

/**
 * Applies Lambert W function. If the input is an array, the function will be performed element-wise.
 * @param {*} x 
 */
function lambertw(x) {
    if (type(x) === "Dual") { //dual number
        var h = Math.sqrt(Number.EPSILON);
        var t1 = (f_lambertw(x.a + h) - f_lambertw(x.a - h)) / (2 * h); //numerical derivative
        return new Dual(f_lambertw(x.a), x.b * t1);
    } else if (type(x) === "NdArray" || type(x) == "Array") { //array
        x = new NdArray(x);
        return new NdArray(applyScalar(f_lambertw, x.value));
    } else { //number
        x = parseFloat(x);
        return f_lambertw(x);
    }
}

/**
 * Factorial. Uses gamma function for non-integers. If the input is an array, the function will be performed element-wise.
 * @param {*} x 
 */
function fac(x) {
    if (type(x) === "Dual") { //dual number
        var h = Math.sqrt(Number.EPSILON);
        var t1 = (fac(x.a + h) - fac(x.a - h)) / (2 * h); //numerical derivative
        return new Dual(fac(x.a), x.b * t1);
    } else if (type(x) === "NdArray" || type(x) == "Array") { //array
        x = new NdArray(x);
        return new NdArray(applyScalar(fac, x.value));
    } else { //number
        x = parseFloat(x);
        if (x >= 0 && x < 20 && x === Math.floor(x)) {
            switch (x) { //Return some preset values for small integers
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
        } else if (x >= 0) {
            //tweaked Ramanujan approximation by Hirschhorn & Villarino
            var n = x;
            var theta = 1 - (11 / (8 * n)) + (79 / (112 * n * n));
            var t1 = Math.sqrt(Math.PI);
            var t2 = Math.pow(n / Math.E, n);
            var t3 = 8 * n * n * n + 4 * n * n + n + theta / 30;
            return t1 * t2 * Math.pow(t3, 1 / 6);
        } else {
            //use Weierstrass's definition for negative numbers
            var z = x + 1;
            var t1 = Math.exp(-euler_gamma * z) / z;
            var t2 = 1;
            for (var i = 1; i < 1000; i++) {
                var u1 = Math.exp(z / i);
                t2 *= Math.pow(1 + (z / i), -1) * u1;
            }
            return t1 * t2;

        }
    }
}



function transpose(array) {
    return array[0].map((__, colIndex) => array.map(row => row[colIndex]));
}

function dot(a, b) {
    return new NdArray(a).dot(new NdArray(b)).value;
}

//taken from http://blog.acipo.com/matrix-inversion-in-javascript/
function matrix_invert(r) { if (r.length === r[0].length) { var f = 0, n = 0, t = 0, e = r.length, o = 0, i = [], g = []; for (f = 0; f < e; f += 1)for (i[i.length] = [], g[g.length] = [], t = 0; t < e; t += 1)i[f][t] = f == t ? 1 : 0, g[f][t] = r[f][t]; for (f = 0; f < e; f += 1) { if (0 == (o = g[f][f])) { for (n = f + 1; n < e; n += 1)if (0 != g[n][f]) { for (t = 0; t < e; t++)o = g[f][t], g[f][t] = g[n][t], g[n][t] = o, o = i[f][t], i[f][t] = i[n][t], i[n][t] = o; break } if (0 == (o = g[f][f])) return } for (t = 0; t < e; t++)g[f][t] = g[f][t] / o, i[f][t] = i[f][t] / o; for (n = 0; n < e; n++)if (n != f) for (o = g[n][f], t = 0; t < e; t++)g[n][t] -= o * g[f][t], i[n][t] -= o * i[f][t] } return i } }

var inv = matrix_invert;

/**
 * Fit a polynomial p(x) = p[0] * x**deg + ... + p[deg] of degree deg to points (x, y). Returns a vector of coefficients p that minimises the squared error in the order deg, deg-1, … 0.
 * @param {*} xData 
 * @param {*} yData 
 * @param {number} order 
 */
function polyfit(xData, yData, order) {
    xData = new NdArray(xData);
    yData = new NdArray(yData);
    var i = 0;

    //taken from https://stackoverflow.com/questions/28269021/how-do-i-create-a-best-fit-polynomial-curve-in-javascript
    var x = xData.value;
    var y = yData.value;


    var xMatrix = [];
    var xTemp = [];
    var yMatrix = transpose([y]);

    for (var j = 0; j < x.length; j++) {
        xTemp = [];
        for (i = 0; i <= order; i++) {
            xTemp.push(1 * Math.pow(x[j % x.length], i));
        }
        xMatrix.push(xTemp);
    }

    // console.log(JSON.stringify(xMatrix),yMatrix);

    var xMatrixT = transpose(xMatrix);
    var dot1 = dot(xMatrixT, xMatrix);
    var dotInv = inv(dot1);
    var dot2 = dot(xMatrixT, yMatrix);
    var solution = dot(dotInv, dot2);
    return new NdArray(solution.map((e) => e[0]));
}

/**
 * Evaluate a polynomial at points x.
 * @param {*} poly 
 * @param {number} num 
 */
function polyval(poly, x) {
    poly = new NdArray(poly);
    var result = 0;
    for (var i = 0; i < poly.shape(); i++) {
        result += poly.get(i) * Math.pow(x, i);
    }

    return result;
}

// var primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249, 1259, 1277, 1279, 1283, 1289, 1291, 1297, 1301, 1303, 1307, 1319, 1321, 1327, 1361, 1367, 1373, 1381, 1399, 1409, 1423, 1427, 1429, 1433, 1439, 1447, 1451, 1453, 1459, 1471, 1481, 1483, 1487, 1489, 1493, 1499, 1511, 1523, 1531, 1543, 1549, 1553, 1559, 1567, 1571, 1579, 1583, 1597, 1601, 1607, 1609, 1613, 1619, 1621, 1627, 1637, 1657, 1663, 1667, 1669, 1693, 1697, 1699, 1709, 1721, 1723, 1733, 1741, 1747, 1753, 1759, 1777, 1783, 1787, 1789, 1801, 1811, 1823, 1831, 1847, 1861, 1867, 1871, 1873, 1877, 1879, 1889, 1901, 1907, 1913, 1931, 1933, 1949, 1951, 1973, 1979, 1987, 1993, 1997, 1999, 2003, 2011, 2017, 2027, 2029, 2039, 2053, 2063, 2069, 2081, 2083, 2087, 2089, 2099, 2111, 2113, 2129, 2131, 2137, 2141, 2143, 2153, 2161, 2179, 2203, 2207, 2213, 2221, 2237, 2239, 2243, 2251, 2267, 2269, 2273, 2281, 2287, 2293, 2297, 2309, 2311, 2333, 2339, 2341, 2347, 2351, 2357, 2371, 2377, 2381, 2383, 2389, 2393, 2399, 2411, 2417, 2423, 2437, 2441, 2447, 2459, 2467, 2473, 2477, 2503, 2521, 2531, 2539, 2543, 2549, 2551, 2557, 2579, 2591, 2593, 2609, 2617, 2621, 2633, 2647, 2657, 2659, 2663, 2671, 2677, 2683, 2687, 2689, 2693, 2699, 2707, 2711, 2713, 2719, 2729, 2731, 2741, 2749, 2753, 2767, 2777, 2789, 2791, 2797, 2801, 2803, 2819, 2833, 2837, 2843, 2851, 2857, 2861, 2879, 2887, 2897, 2903, 2909, 2917, 2927, 2939, 2953, 2957, 2963, 2969, 2971, 2999, 3001, 3011, 3019, 3023, 3037, 3041, 3049, 3061, 3067, 3079, 3083, 3089, 3109, 3119, 3121, 3137, 3163, 3167, 3169, 3181, 3187, 3191, 3203, 3209, 3217, 3221, 3229, 3251, 3253, 3257, 3259, 3271, 3299, 3301, 3307, 3313, 3319, 3323, 3329, 3331, 3343, 3347, 3359, 3361, 3371, 3373, 3389, 3391, 3407, 3413, 3433, 3449, 3457, 3461, 3463, 3467, 3469, 3491, 3499, 3511, 3517, 3527, 3529, 3533, 3539, 3541, 3547, 3557, 3559, 3571, 3581, 3583, 3593, 3607, 3613, 3617, 3623, 3631, 3637, 3643, 3659, 3671, 3673, 3677, 3691, 3697, 3701, 3709, 3719, 3727, 3733, 3739, 3761, 3767, 3769, 3779, 3793, 3797, 3803, 3821, 3823, 3833, 3847, 3851, 3853, 3863, 3877, 3881, 3889, 3907, 3911, 3917, 3919, 3923, 3929, 3931, 3943, 3947, 3967, 3989, 4001, 4003, 4007, 4013, 4019, 4021, 4027, 4049, 4051, 4057, 4073, 4079, 4091, 4093, 4099, 4111, 4127, 4129, 4133, 4139, 4153, 4157, 4159, 4177, 4201, 4211, 4217, 4219, 4229, 4231, 4241, 4243, 4253, 4259, 4261, 4271, 4273, 4283, 4289, 4297, 4327, 4337, 4339, 4349, 4357, 4363, 4373, 4391, 4397, 4409, 4421, 4423, 4441, 4447, 4451, 4457, 4463, 4481, 4483, 4493, 4507, 4513, 4517, 4519, 4523, 4547, 4549, 4561, 4567, 4583, 4591, 4597, 4603, 4621, 4637, 4639, 4643, 4649, 4651, 4657, 4663, 4673, 4679, 4691, 4703, 4721, 4723, 4729, 4733, 4751, 4759, 4783, 4787, 4789, 4793, 4799, 4801, 4813, 4817, 4831, 4861, 4871, 4877, 4889, 4903, 4909, 4919, 4931, 4933, 4937, 4943, 4951, 4957, 4967, 4969, 4973, 4987, 4993, 4999, 5003, 5009, 5011, 5021, 5023, 5039, 5051, 5059, 5077, 5081, 5087, 5099, 5101, 5107, 5113, 5119, 5147, 5153, 5167, 5171, 5179, 5189, 5197, 5209, 5227, 5231, 5233, 5237, 5261, 5273, 5279, 5281, 5297, 5303, 5309, 5323, 5333, 5347, 5351, 5381, 5387, 5393, 5399, 5407, 5413, 5417, 5419, 5431, 5437, 5441, 5443, 5449, 5471, 5477, 5479, 5483, 5501, 5503, 5507, 5519, 5521, 5527, 5531, 5557, 5563, 5569, 5573, 5581, 5591, 5623, 5639, 5641, 5647, 5651, 5653, 5657, 5659, 5669, 5683, 5689, 5693, 5701, 5711, 5717, 5737, 5741, 5743, 5749, 5779, 5783, 5791, 5801, 5807, 5813, 5821, 5827, 5839, 5843, 5849, 5851, 5857, 5861, 5867, 5869, 5879, 5881, 5897, 5903, 5923, 5927, 5939, 5953, 5981, 5987, 6007, 6011, 6029, 6037, 6043, 6047, 6053, 6067, 6073, 6079, 6089, 6091, 6101, 6113, 6121, 6131, 6133, 6143, 6151, 6163, 6173, 6197, 6199, 6203, 6211, 6217, 6221, 6229, 6247, 6257, 6263, 6269, 6271, 6277, 6287, 6299, 6301, 6311, 6317, 6323, 6329, 6337, 6343, 6353, 6359, 6361, 6367, 6373, 6379, 6389, 6397, 6421, 6427, 6449, 6451, 6469, 6473, 6481, 6491, 6521, 6529, 6547, 6551, 6553, 6563, 6569, 6571, 6577, 6581, 6599, 6607, 6619, 6637, 6653, 6659, 6661, 6673, 6679, 6689, 6691, 6701, 6703, 6709, 6719, 6733, 6737, 6761, 6763, 6779, 6781, 6791, 6793, 6803, 6823, 6827, 6829, 6833, 6841, 6857, 6863, 6869, 6871, 6883, 6899, 6907, 6911, 6917, 6947, 6949, 6959, 6961, 6967, 6971, 6977, 6983, 6991, 6997, 7001, 7013, 7019, 7027, 7039, 7043, 7057, 7069, 7079, 7103, 7109, 7121, 7127, 7129, 7151, 7159, 7177, 7187, 7193, 7207, 7211, 7213, 7219, 7229, 7237, 7243, 7247, 7253, 7283, 7297, 7307, 7309, 7321, 7331, 7333, 7349, 7351, 7369, 7393, 7411, 7417, 7433, 7451, 7457, 7459, 7477, 7481, 7487, 7489, 7499, 7507, 7517, 7523, 7529, 7537, 7541, 7547, 7549, 7559, 7561, 7573, 7577, 7583, 7589, 7591, 7603, 7607, 7621, 7639, 7643, 7649, 7669, 7673, 7681, 7687, 7691, 7699, 7703, 7717, 7723, 7727, 7741, 7753, 7757, 7759, 7789, 7793, 7817, 7823, 7829, 7841, 7853, 7867, 7873, 7877, 7879, 7883, 7901, 7907, 7919, 7927, 7933, 7937, 7949, 7951, 7963, 7993, 8009, 8011, 8017, 8039, 8053, 8059, 8069, 8081, 8087, 8089, 8093, 8101, 8111, 8117, 8123, 8147, 8161, 8167, 8171, 8179, 8191, 8209, 8219, 8221, 8231, 8233, 8237, 8243, 8263, 8269, 8273, 8287, 8291, 8293, 8297, 8311, 8317, 8329, 8353, 8363, 8369, 8377, 8387, 8389, 8419, 8423, 8429, 8431, 8443, 8447, 8461, 8467, 8501, 8513, 8521, 8527, 8537, 8539, 8543, 8563, 8573, 8581, 8597, 8599, 8609, 8623, 8627, 8629, 8641, 8647, 8663, 8669, 8677, 8681, 8689, 8693, 8699, 8707, 8713, 8719, 8731, 8737, 8741, 8747, 8753, 8761, 8779, 8783, 8803, 8807, 8819, 8821, 8831, 8837, 8839, 8849, 8861, 8863, 8867, 8887, 8893, 8923, 8929, 8933, 8941, 8951, 8963, 8969, 8971, 8999, 9001, 9007, 9011, 9013, 9029, 9041, 9043, 9049, 9059, 9067, 9091, 9103, 9109, 9127, 9133, 9137, 9151, 9157, 9161, 9173, 9181, 9187, 9199, 9203, 9209, 9221, 9227, 9239, 9241, 9257, 9277, 9281, 9283, 9293, 9311, 9319, 9323, 9337, 9341, 9343, 9349, 9371, 9377, 9391, 9397, 9403, 9413, 9419, 9421, 9431, 9433, 9437, 9439, 9461, 9463, 9467, 9473, 9479, 9491, 9497, 9511, 9521, 9533, 9539, 9547, 9551, 9587, 9601, 9613, 9619, 9623, 9629, 9631, 9643, 9649, 9661, 9677, 9679, 9689, 9697, 9719, 9721, 9733, 9739, 9743, 9749, 9767, 9769, 9781, 9787, 9791, 9803, 9811, 9817, 9829, 9833, 9839, 9851, 9857, 9859, 9871, 9883, 9887, 9901, 9907, 9923, 9929, 9931, 9941, 9949, 9967, 9973];

/**
 * Matrix square root.
 * @param {*} x 
 */
function sqrtm(x) {
    x = new NdArray(x);
    assert(x.shape()[0] === x.shape()[1] && x.ndim() === 2)

    var y = x;
    var z = identity(x.shape()[0]);
    for (var k = 0; k < 50; k++) {
        y_old = y;
        z_old = z;
        try {
            y = y_old.add(inv(z_old.value)).mul(0.5);
            z = z_old.add(inv(y_old.value)).mul(0.5);
        } catch (e) {
            if (e instanceof assert.AssertionError) {
                console.log("(Warning) Denman–Beavers iteration may be poorly conditioned.")
            } else {
                throw e;
            }

        }
    }

    return y;
}

var twopi = 2 * Math.PI;
function fourier(s, P, N = 50, q = 0) {
    function an(n) {
        var t1 = 2 / P;
        var t2 = integral((x) => {
            return s(x) * Math.cos(twopi * x * (n / P));
        }, q - (P / 2), q + (P / 2));
        return t1 * t2;
    }

    function bn(n) {
        var t1 = 2 / P;
        var t2 = integral((x) => {
            return s(x) * Math.sin(twopi * x * (n / P));
        }, q - (P / 2), q + (P / 2));
        return t1 * t2;
    }

    var result = [[], []];
    for (var i = 0; i < N; i++) {
        result[0].push(an(i));
    }

    for (var j = 0; j < N; j++) {
        result[1].push(bn(j));
    }

    return new NdArray(result);
}

function getStandardDeviation(array) {
    const n = array.length
    const mean = array.reduce((a, b) => a + b) / n
    return Math.sqrt(array.map(x => Math.pow(x - mean, 2)).reduce((a, b) => a + b) / n)
}


function useExp(f) {
    var ratios = [];
    for (var i = 0; i < 50; i++) {
        //Use a trycatch to dodge MathDomainError
        if (isFinite(f(i + 1)) && isFinite(f(i))) {
            ratios.push(f(i + 1) / f(i))
        }
    }

    var stdev = getStandardDeviation(ratios);
    var amin = Math.min(...ratios);
    if (stdev < 1) {
        return true;
    } else {
        return false;
    }
}

function approx(f, n = 20) {
    if (useExp(f)) {
        var xData = [];
        var yData = [];
        for (var i = -50; i < 50; i += 0.2) {
            if (isFinite(Math.log(f(i)))) {
                xData.push(i)
                yData.push(Math.log(f(i)));
            }
        }

        return { "value": polyfit(xData, yData, 1), "model": "exp" };
    } else {
        var xData = [];
        var yData = [];
        for (var i = -50; i < 50; i += 0.2) {
            if (isFinite(Math.log(f(i)))) {
                xData.push(i)
                yData.push(f(i));
            }
        }

        return { "value": polyfit(xData, yData, n), "model": "poly" };
    }
}


// function firstDeriv(f, x, n) {
//     function f_(i, a, h) {
//         return f(a + i * h);
//     }

//     //List of finite differences

//     var ders = [
//         f,
//         (a, h) => { return ((1) / (5544) * f_(-6, a, h) - (1) / (385) * f_(-5, a, h) + (1) / (56) * f_(-4, a, h) - (5) / (63) * f_(-3, a, h) + (15) / (56) * f_(-2, a, h) - (6) / (7) * f_(-1, a, h) + (6) / (7) * f_(1, a, h) - (15) / (56) * f_(2, a, h) + (5) / (63) * f_(3, a, h) - (1) / (56) * f_(4, a, h) + (1) / (385) * f_(5, a, h) - (1) / (5544) * f_(6, a, h)) / (h ** 1) },
//         (a, h) => { return (-(1) / (16632) * f_(-6, a, h) + (2) / (1925) * f_(-5, a, h) - (1) / (112) * f_(-4, a, h) + (10) / (189) * f_(-3, a, h) - (15) / (56) * f_(-2, a, h) + (12) / (7) * f_(-1, a, h) - (5369) / (1800) * f_(0, a, h) + (12) / (7) * f_(1, a, h) - (15) / (56) * f_(2, a, h) + (10) / (189) * f_(3, a, h) - (1) / (112) * f_(4, a, h) + (2) / (1925) * f_(5, a, h) - (1) / (16632) * f_(6, a, h)) / (h ** 2) },
//         (a, h) => { return (-(479) / (302400) * f_(-6, a, h) + (19) / (840) * f_(-5, a, h) - (643) / (4200) * f_(-4, a, h) + (4969) / (7560) * f_(-3, a, h) - (4469) / (2240) * f_(-2, a, h) + (1769) / (700) * f_(-1, a, h) - (1769) / (700) * f_(1, a, h) + (4469) / (2240) * f_(2, a, h) - (4969) / (7560) * f_(3, a, h) + (643) / (4200) * f_(4, a, h) - (19) / (840) * f_(5, a, h) + (479) / (302400) * f_(6, a, h)) / (h ** 3) },
//         (a, h) => { return ((479) / (453600) * f_(-6, a, h) - (19) / (1050) * f_(-5, a, h) + (643) / (4200) * f_(-4, a, h) - (4969) / (5670) * f_(-3, a, h) + (4469) / (1120) * f_(-2, a, h) - (1769) / (175) * f_(-1, a, h) + (37037) / (2700) * f_(0, a, h) - (1769) / (175) * f_(1, a, h) + (4469) / (1120) * f_(2, a, h) - (4969) / (5670) * f_(3, a, h) + (643) / (4200) * f_(4, a, h) - (19) / (1050) * f_(5, a, h) + (479) / (453600) * f_(6, a, h)) / (h ** 4) },
//         (a, h) => { return ((139) / (12096) * f_(-6, a, h) - (121) / (756) * f_(-5, a, h) + (3125) / (3024) * f_(-4, a, h) - (3011) / (756) * f_(-3, a, h) + (33853) / (4032) * f_(-2, a, h) - (1039) / (126) * f_(-1, a, h) + (1039) / (126) * f_(1, a, h) - (33853) / (4032) * f_(2, a, h) + (3011) / (756) * f_(3, a, h) - (3125) / (3024) * f_(4, a, h) + (121) / (756) * f_(5, a, h) - (139) / (12096) * f_(6, a, h)) / (h ** 5) },
//         (a, h) => { return (-(139) / (12096) * f_(-6, a, h) + (121) / (630) * f_(-5, a, h) - (3125) / (2016) * f_(-4, a, h) + (3011) / (378) * f_(-3, a, h) - (33853) / (1344) * f_(-2, a, h) + (1039) / (21) * f_(-1, a, h) - (44473) / (720) * f_(0, a, h) + (1039) / (21) * f_(1, a, h) - (33853) / (1344) * f_(2, a, h) + (3011) / (378) * f_(3, a, h) - (3125) / (2016) * f_(4, a, h) + (121) / (630) * f_(5, a, h) - (139) / (12096) * f_(6, a, h)) / (h ** 6) },
//         (a, h) => { return (-(31) / (480) * f_(-6, a, h) + (41) / (48) * f_(-5, a, h) - (601) / (120) * f_(-4, a, h) + (755) / (48) * f_(-3, a, h) - (885) / (32) * f_(-2, a, h) + (971) / (40) * f_(-1, a, h) - (971) / (40) * f_(1, a, h) + (885) / (32) * f_(2, a, h) - (755) / (48) * f_(3, a, h) + (601) / (120) * f_(4, a, h) - (41) / (48) * f_(5, a, h) + (31) / (480) * f_(6, a, h)) / (h ** 7) },
//         (a, h) => { return ((31) / (360) * f_(-6, a, h) - (41) / (30) * f_(-5, a, h) + (601) / (60) * f_(-4, a, h) - (755) / (18) * f_(-3, a, h) + (885) / (8) * f_(-2, a, h) - (971) / (5) * f_(-1, a, h) + (7007) / (30) * f_(0, a, h) - (971) / (5) * f_(1, a, h) + (885) / (8) * f_(2, a, h) - (755) / (18) * f_(3, a, h) + (601) / (60) * f_(4, a, h) - (41) / (30) * f_(5, a, h) + (31) / (360) * f_(6, a, h)) / (h ** 8) },
//         (a, h) => { return ((1) / (4) * f_(-6, a, h) - 3 * f_(-5, a, h) + 15 * f_(-4, a, h) - 41 * f_(-3, a, h) + (261) / (4) * f_(-2, a, h) - 54 * f_(-1, a, h) + 54 * f_(1, a, h) - (261) / (4) * f_(2, a, h) + 41 * f_(3, a, h) - 15 * f_(4, a, h) + 3 * f_(5, a, h) - (1) / (4) * f_(6, a, h)) / (h ** 9) },
//     ]



//     function C(d) {
//         return ders[n](x, d);
//     }

//     function D(d) {
//         return (4 * C(d) - C(2 * d)) / 3;
//     }

//     function E(d) {
//         return (16 * D(d) - D(2 * d)) / 15;
//     }

//     function F(d) {
//         return (256 * E(d) - E(2 * d)) / 255;
//     }

//     function G(d) {
//         return (1024 * F(d) - F(2 * d)) / 1023;
//     }

//     return G(1.5e-9);
// }

// Finds primes by Sieve  
    // of Eratosthenes method 
    function getPrimes(n) 
    { 
        var i, j; 
        var isPrime = new Array(n + 1); 
          
        for(i = 0; i < n + 1; i++) 
            isPrime[i] = 1; 
          
        for (i = 2; i * i <= n; i++) 
        {      
            // If isPrime[i] is not  
            // changed, then it is prime 
            if (isPrime[i] == 1) 
            { 
                // Update all  
                // multiples of p 
                for (j = i * 2; j <= n; j += i) 
                    isPrime[j] = 0; 
            } 
        } 
      
        // Forming array of the  
        // prime numbers found 
        var primes = new Array(); 
        for (i = 2; i <= n; i++) 
            if (isPrime[i] == 1) 
                primes.push(i); 
        return primes; 
    } 
      
    /**
     * Checking whether a number is k-rough or not.
     * @param {number} n 
     * @param {number} k 
     */
    function isRough(n, k) 
    { 
        [n,k] = [parseFloat(n),parseFloat(k)];
        var primes = getPrimes(n); 
          
        // Finding minimum 
        // prime factor of n 
        var min_pf = n; 
        for (var i = 0; i < primes.length; i++) 
            if (n % primes[i] == 0) 
                min_pf = primes[i];
      
        // Return true if minimum  
        // prime factor is greater 
        // than or equal to k. Else 
        // return false. 
        return (min_pf >= k); 
    } 
     

/**
 * Returns the absolute value of method.
 * @param {*} x 
 */
function abs(x) {
    if (type(x) === "Dual") { //dual number
        var h = Math.sqrt(Number.EPSILON);
        var t1 = (abs(x.a + h) - abs(x.a - h)) / (2 * h); //numerical derivative
        return new Dual(abs(x.a), x.b * t1);
    } else if (type(x) === "NdArray" || type(x) == "Array") { //array
        x = new NdArray(x);
        return new NdArray(applyScalar(abs, x.value));
    } else { //number
        x = parseFloat(x);
        return Math.abs(x);
    }
}


/** 
 * Create a Hilbert matrix of order n.
 */
function hilbert(n) {
    n = parseFloat(n);
    var result = [];
    for(var i = 1; i <= n; i++) {
        result.push([]);
        for(var j = 1; j <= n; j++) {
            result[i-1][j-1] = 1/(i+j-1);
        }
    }

    return new NdArray(result);
}
//Alias
var factorial = fact = fac;
var euler_gamma = 0.5772156649015329;
var exponential = exp;
var rint = round;

var _ = new (function () { //private methods
    this.polyfit = polyfit;
    this.polyval = polyval;
    this.sqrtm = sqrtm;
    // this.approx = approx;
    this.Int = Int;
    // this.float = float;
    // this.Complex = Complex;

})();

Object.assign(_,{
    size,
    zeros,
    ones,
    full,
    arange,
    sin,
    cos,
    tan,
    asin,
    acos,
    atan,
    exp,
    log,
    sqrt,
    cbrt,
    floor,
    ceil,
    round,
    lambertw,
    integral,
    euler_gamma,
    rint,
    exponential,
    fac,
    fact,
    factorial,
    identity,
    isRough,
    hilbert
});


module.exports = _;