var NdArray = require("./NdArray.js");
var misc = require("./misc.js");
var random = new (function () {
    /**
    * Random values in a given shape.
    @param {number|number[]} shape
    */
    function rand(shape) {
        var result = NdArray._.applyScalar(Math.random, misc.zeros(shape).tolist());
        return new NdArray(result);
    }

    /**
     * Approximately gaussian random numbers between 0 and 1.
     */
    function gaussianRand() {
        var rand = 0;
        for (var i = 0; i < 6; i += 1) {
            rand += Math.random();
        }

        return rand / 6;
    }

    this.rand = rand;
    this.gaussianRand = gaussianRand;
})();

module.exports = random;