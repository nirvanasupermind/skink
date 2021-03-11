// lynx Library
// Copyright (c) nirvanasupermind
// Usage permitted under terms of MIT License

"use strict";

var assert = require("assert");
if (!Math.floorMod) {
    Math.floorMod = function (a, b) {
        return Math.sign(b) * (Math.abs(a) % Math.abs(b));

    }
}

//From https://stackoverflow.com/questions/55420156/get-arrays-depth-in-javascript
function getArrayDepth(value) {
    return Array.isArray(value) ?
        1 + Math.max(...value.map(getArrayDepth)) :
        0;
}


// var CONTEXT = {};
//safer version of eval
function safeEval(obj) {
    return new Function('"use strict";' + obj)();
}

//from https://gist.github.com/jremmen/9454479
function dotproduct(a, b) {
    return a.map(function (x, i) {
        return a[i] * b[i];
    }).reduce(function (m, n) { return m + n; });
}

function transpose(a) {
    return a[0].map(function (x, i) {
        return a.map(function (y, k) {
            return y[i];
        })
    });
}

//from 
const multiplyMatrices = (a, b) => {
    if (!Array.isArray(a) || !Array.isArray(b) || !a.length || !b.length) {
        throw new Error('arguments should be in 2-dimensional array format');
    }
    let x = a.length,
        z = a[0].length,
        y = b[0].length;
    //    if (b.length !== z) {
    //       // XxZ & ZxY => XxY
    //       throw new Error('number of columns in the first matrix should be the same as the number of rows in the second');
    //    }
    let productRow = Array.apply(null, new Array(y)).map(Number.prototype.valueOf, 0);
    let product = new Array(x);
    for (let p = 0; p < x; p++) {
        product[p] = productRow.slice();
    }
    for (let i = 0; i < x; i++) {
        for (let j = 0; j < y; j++) {
            for (let k = 0; k < z; k++) {
                product[i][j] += a[i][k] * b[k][j];
            }
        }
    }
    return product;
}

function explode(a, b = 80, c = "\n") {
    return a.match(new RegExp(".{0," + b + "}", "g")).slice(0, -1).join(c);
}

//numpy-style pretty printing
function stringify(value, indent = 4) {
    if (getArrayDepth(value) === 1)
        return JSON.stringify(value);

    if (value.length === 1)
        return "[" + stringify(value[0]) + "]";

    var result = "[" + JSON.stringify(value[0]) + ",";
    for (var i = 1; i < value.length - 1; i++) {
        result += "\n" + " ".repeat(indent) + JSON.stringify(value[i]) + ",";
    }
    result += "\n" + " ".repeat(indent) + JSON.stringify(value[value.length - 1])
    result += "]";
    return result;
}


var getStackTrace = function () {
    var obj = {};
    Error.captureStackTrace(obj, getStackTrace);
    return obj.stack;
};

//Get dimensions of array
function shape(value) {
    value = list(value);
    if (type(value) === "Number") {
        //Scalars have a length of 1
        return 1;
    } else if (value + "" === "") {
        return [0];
    } else if (getArrayDepth(value) === 1) {
        return [value.length];
    } else {
        return shape(value.map((e) => e[0]).filter((e) => e !== undefined)).concat(shape(value[0]))
    }
}

//Convert to list/array
function list(x) {
    if (type(x) === "NdArray")
        return x.value
    if (type(x) !== "Array")
        return [x];
    return x;
}

//Applies a function element-wise on two tensors
function apply(f, x, y) {
    assert(shape(x).toString() === shape(y).toString()); //must have the same shape
    if (getArrayDepth(x) === 1) {
        return x.map((a, b) => f(a, y[b]));
    } else {
        //Recursive call
        return x.map((a, b) => {
            return apply(f, a, y[b]);
        });
    }
}

//Applies a function element-wise on tensor and scalar
function applyScalar(f, x) {
    if (getArrayDepth(x) === 1) {
        return x.map((a) => f(a));
    } else {
        //Recursive call
        return x.map((a) => applyScalar(f, a));
    }
}

//Version of "typeof" that works for objects
function type(x) {
    if (x === null || x === undefined)
        return "Null"
    return x.constructor.name;
}


/**
 * The constructor for NdArray. It takes an Array and returns the corresponding NdArray.
 * @param {any[]} value 
 */
function NdArray(value) {
    if (!(this instanceof NdArray)) {
        return new NdArray(value);
    } else if (value instanceof NdArray) {
        //Clone
        this.value = value.value;
    } else {
        value = list(value);
        assert(new Set(value.map(shape).map(String)).size <= 1); //Validate the array
        this.value = applyScalar(parseFloat, value);
    }
}





/**
 * Return the shape of an array.
 */
NdArray.prototype.shape = function () {
    return shape(this.value);
}

/**
 * Return the number of dimensions of an array.
 */
NdArray.prototype.ndim = function () {
    return getArrayDepth(this.value);
}


function replaceNegatives(x, y) {
    x = list(x);
    return x.map((e) => (e < 0 ? y + e : e));
}
/**
 * Returns an element of an NdArray at a given index. 
 * It is 0-based, and accepts negative indices for indexing from the end of the array.
 */
NdArray.prototype.get = function (...n) {
    n = replaceNegatives(n, this.shape()[n.length - 1]);
    var result = this.value;
    for (var i = 0; i < n.length; i++) {
        result = result[n[i]];
    }
    console.log(result);
    if(Array.isArray(result)) { 
        result = new NdArray(result);
    }

    return result;
}

function cleanup(a) {
    return JSON.parse(JSON.stringify(a)).filter((e) => type(e) !== "Null");
}

/**
 * Sets an element of an NdArray to a new value. 
 */
NdArray.prototype.set = function (...m) {
    var n = m.slice(0, -1);
    n = replaceNegatives(n, this.shape()[n.length - 1]);
    var subscript = n.map((e) => "[" + e + "]").join("");
    this.value = new NdArray(cleanup(safeEval("var a = " + JSON.stringify(this.value) + ";a" + subscript + "=" + JSON.stringify(m[m.length - 1]) + ";return a;"))).value;
    return m[m.length - 1];
}

/**
 * Element-wise addition.
 */
NdArray.prototype.add = function (that) {
    if (type(that) === "Number") { //Scalar
        return new NdArray(applyScalar((a) => a + that, this.value));
    } else {
        that = new NdArray(that);
        return new NdArray(apply((a, b) => a + b, this.value, that.value));
    }
}

/**
 * Element-wise subtraction.
 */
NdArray.prototype.sub = function (that) {
    if (type(that) === "Number") { //Scalar
        return new NdArray(applyScalar((a) => a - that, this.value));
    } else {
        that = new NdArray(that);
        return new NdArray(apply((a, b) => a - b, this.value, that.value));
    }
}

/**
 * Element-wise multiplication.
 */
NdArray.prototype.mul = function (that) {
    if (type(that) === "Number") { //Scalar
        return new NdArray(applyScalar((a) => a * that, this.value));
    } else {
        that = new NdArray(that);
        return new NdArray(apply((a, b) => a * b, this.value, that.value));
    }
}


/**
 * Element-wise division.
 */
NdArray.prototype.div = function (that) {
    if (type(that) === "Number") { //Scalar
        return new NdArray(applyScalar((a) => a / that, this.value));
    } else {
        that = new NdArray(that);
        return new NdArray(apply((a, b) => a / b, this.value, that.value));
    }
}

/**
 * Element-wise modulo.
 */
NdArray.prototype.mod = function (that) {
    if (type(that) === "Number") { //Scalar
        return new NdArray(applyScalar((a) => a % that, this.value));
    } else {
        that = new NdArray(that);
        return new NdArray(apply((a, b) => a % b, this.value, that.value));
    }
}

/**
 * Element-wise floor modulo.
 */
NdArray.prototype.mod = function (that) {
    if (type(that) === "Number") { //Scalar
        return new NdArray(applyScalar((a) => floorMod(a,that), this.value));
    } else {
        that = new NdArray(that);
        return new NdArray(apply(floorMod, this.value, that.value));
    }
}


/**
 * Dot product of two arrays. Currently, it does not support 3D and higher input.
 */
NdArray.prototype.dot = function (that) {
    if (type(that) !== "Number")
        that = new NdArray(that);
    if (type(that) === "Number") { //Scalar
        return new NdArray(applyScalar((a) => a * that, this.value));
    } else if (this.ndim() === 1 && that.ndim() === 1) { //Vector
        assert(String(this.shape()) === String(that.shape()));
        return dotproduct(this.value, that.value);
    } else { //Matrix
        if (this.shape()[1] && that.shape()[0]) { assert(this.shape()[1] === that.shape()[0]) }
        return new NdArray(multiplyMatrices(this.value, that.value));
    }
}


/**
 * Return the minimum.
 */

NdArray.prototype.min = function () {
    return Math.min(...[].concat.apply([], this.value))
}


/**
 * Return the maximum.
 */

NdArray.prototype.max = function () {
    return Math.max(...[].concat.apply([], this.value))
}


/**
 * Converts the array to Array.
 */
NdArray.prototype.tolist = function () {
    return this.value;
}

NdArray.prototype.toString = function () {
    return "array(" + stringify(this.value) + ")";
}



//Alias
NdArray.prototype.plus = NdArray.prototype.add;
NdArray.prototype.minus = NdArray.prototype.sub;
NdArray.prototype.times = NdArray.prototype.multiply = NdArray.prototype.mul;
NdArray.prototype.divide = NdArray.prototype.div;
NdArray.prototype.modular = NdArray.prototype.mod;

NdArray._ = {}; //private methods
NdArray._.applyScalar = applyScalar;
NdArray._.type = type;
NdArray._.list = list;
// NdArray._.zeros = zeros;

module.exports = NdArray;