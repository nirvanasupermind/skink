/*
This module for implementing all the types not already accessible, and some helper methods.
 */
//  Does not work with `new (funcA.bind(thisArg, args))`
var Environment = require("./Environment.js")
// UTIL
if (!Function.prototype.bind) (function () {
    var slice = Array.prototype.slice;
    Function.prototype.bind = function () {
        var thatFunc = this, thatArg = arguments[0];
        var args = slice.call(arguments, 1);
        if (typeof thatFunc !== 'function') {
            // closest thing possible to the ECMAScript 5
            // internal IsCallable function
            throw new TypeError('Function.prototype.bind - ' +
                'what is trying to be bound is not callable');
        }
        return function () {
            var funcArgs = args.concat(slice.call(arguments))
            return thatFunc.apply(thatArg, funcArgs);
        };
    };
})();

function clone(obj) {
    if (obj == null || typeof (obj) != 'object')
        return obj;
    var temp = new obj.constructor();
    var foo = {};
    for (var i = 0; i < Object.getOwnPropertyNames(obj).length; i++) {
        foo[Object.getOwnPropertyNames(obj)[i]] = obj[Object.getOwnPropertyNames(obj)[i]];
    }

    for (var key in foo)
        temp[key] = clone(foo[key]);
    return temp;
}

Object.prototype.clone = function () {
    return clone(this);
}

const getCircularReplacer = () => {
  const seen = new WeakSet();
  return (key, value) => {
    if (typeof value === "object" && value !== null) {
      if (seen.has(value)) {
        return "[Circular]";
      }
      seen.add(value);
    }
    return value;
  };
};



var lynx = require("lynx-js"); //Import the lynx dependency


var Int = lynx.Int._.int(32); //Int32
var Long = lynx.Int.bind({}); //Int64

module.exports = { Int, Long, getCircularReplacer }