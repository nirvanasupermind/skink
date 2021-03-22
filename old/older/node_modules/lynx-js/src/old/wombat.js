var misc = require("./misc.js");
var Dual = require("./dual.js");
// var Vector = require("./vector.js");
var Matrix = require("./matrix.js");
/**
 * The Wombat module.
 */
var wombat = new (function () {
    this.Dual = Dual;
    // this.Vector = Vector;
    this.Matrix = Matrix;
    //Add misc
    Object.assign(this, misc);
})();


module.exports = wombat;