// lynx Library
// Copyright (c) nirvanasupermind
// Usage permitted under terms of MIT License


/**
 * The constructor for Dual. Takes two numbers representing the real and imaginary part of the value.
 * @param {number} a 
 * @param {number} b
 */
function Dual(a, b = 0) {
    if (!(this instanceof Dual)) {
        return new Dual(a, b);
    } else if (a === undefined && b === undefined) {
        this.a = 0;
        this.b = 0;
    } else if (a instanceof Dual) {
        //Clone
        this.a = a.a;
        this.b = a.b;
    } else {
        this.a = parseFloat(a);
        this.b = parseFloat(b);
    }
}

/**
 * Addition.
 */
Dual.prototype.add = function (that) {
    that = new Dual(that);
    return new Dual(this.a + that.a, this.b + that.b);
}

/**
 * Subtraction.
 */
Dual.prototype.sub = function (that) {
    that = new Dual(that);
    return new Dual(this.a - that.a, this.b - that.b);
}

/**
 * Multiplication.
 */
Dual.prototype.mul = function (that) {
    that = new Dual(that);
    var a = this.a, b = this.b, c = that.a, d = that.b;
    return new Dual(a * c, a * d + b * c);
}

/**
 * Division.
 */
Dual.prototype.div = function (that) {
    that = new Dual(that);
    var a = this.a, b = this.b, c = that.a, d = that.b;
    return new Dual(a / c, (b * c - a * d) / (c * c));
}

Dual._ = {}; //Private methods
Dual._.exp = function (x) {
    x = new Dual(x);
    return new Dual(Math.exp(x.a), x.b * Math.exp(x.a))
}

Dual._.ln = function (x) {
    x = new Dual(x);
    return new Dual(Math.log(x.a), x.b / x.a);
}

/**
 * Exponentiation.
 */
Dual.prototype.pow = function (that) {
    that = new Dual(that);
    return Dual._.exp(that.mul(Dual._.ln(this)))
}


Dual.prototype.toString = function () {
    var theSign = (this.b < 0 ? "-" : "+");
    if (this.a === 0)
        return this.b + "E";

    return this.a + theSign + Math.abs(this.b) + "E";
}

//Alias
Dual.prototype.plus = Dual.prototype.add;
Dual.prototype.minus = Dual.prototype.sub;
Dual.prototype.times = Dual.prototype.multiply = Dual.prototype.mul;
Dual.prototype.divide = Dual.prototype.div;

module.exports = Dual;