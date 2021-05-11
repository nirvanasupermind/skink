var NdArray = require("./NdArray.js");
//taken from http://jsfiddle.net/kkf43/
function multiply(array) {
    var result = 1;
    for (var i = 0; i < array.length; i++) {
        result = result * array[i];
    }

    return result;
}

var random = new function () {
    /**
    * Create an array of the given shape and populate it with random samples from a uniform distribution over [0, 1).
    * @param {number[]} shape 
    */
    this.random = function (shape) {
            shape = [...shape];
            return new NdArray(new Array(multiply(shape)).join(null).split(null).map(Math.random), shape)
    }
}

module.exports = random;