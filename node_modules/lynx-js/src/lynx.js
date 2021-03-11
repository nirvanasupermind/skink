// lynx Library
// Copyright (c) nirvanasupermind
// Usage permitted under terms of MIT License

"use strict";

var NdArray = require("./NdArray.js");
var Dual = require("./Dual.js")
var misc = require("./misc.js");
var random = require("./random.js")
//The Lynx module
var lynx = new (function () {
    this.NdArray = NdArray;
    this.Dual = Dual;
    this.random = random;
    Object.assign(this,misc); //add misc
})();


module.exports = lynx;