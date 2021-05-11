//nightjar Library
//Usage permitted under terms of MIT License

var ints = require("./ints.js");
var NdArray = require("./NdArray.js");
var random = require("./random.js");

//taken from http://jsfiddle.net/kkf43/
function multiply(array) {
    var result = 1;
    for (var i = 0; i < array.length; i++) {
        result = result * array[i];
    }

    return result;
}

//the nightjar module
var nightjar = new function () {
    //Classes
    this.Int32 = ints.Int32;
    this.Int64 = ints.Int64;
    this.NdArray = NdArray;
    // this.random = random;        


}

module.exports = nightjar;