var eps = "E"/*"\u03B5"*/;
/**
 * Creates a dual number of the form a+bE
 * @param {number} a 
 * @param {number} b 
 */
function Dual(a, b = 0) {
    if (!(this instanceof Dual)) {
        return new Dual(val);
    } else if (a instanceof Dual) {
        Object.assign(this, a);
    } else {
        this.a = parseFloat(a);
        this.b = parseFloat(b);
    }
}

/**
 * Adds two dual numbers.
 */
Dual.prototype.add = function (that) {
    that = new Dual(that);
    return new Dual(this.a + that.a, this.b + that.b);
}

/**
 * Subtracts two dual numbers.
 */

Dual.prototype.sub = function (that) {
    that = new Dual(that);
    return new Dual(this.a - that.a, this.b - that.b);
}

/**
 * Multiplies two dual numbers.
 */
Dual.prototype.mul = function (that) {
    that = new Dual(that);
    var a = this.a,
        b = this.b,
        c = that.a,
        d = that.b;
    return new Dual(a * c, a * d + b * c);
}


/**
 * Divides two dual numbers.
 */
Dual.prototype.div = function (that) {
    that = new Dual(that)
    var a = this.a,
        b = this.b,
        c = that.a,
        d = that.b;
    return new Dual(a / c, (b * c - a * d) / (c * c));
}

/**
 * Negates a dual number.
 */

Dual.prototype.neg = function () {
    return this.mul(-1);
}

//Helper function to compute natural logarithm
Dual.prototype.ln = function () {
    var a = this.a,
        b = this.b

    return new Dual(Math.log(a), b / a);
}

//Helper to compute integer power
function pow(x, y) {
    if (y === 0) {
        return new Dual(1);
    } else {
        return pow(x, y - 1).mul(x);
    }
}

//Q&D recursive factorial
function fac_rec(a) {
    if (a === 0) {
        return 1;
    } else {
        return a * fac_rec(a - 1);
    }
}
/**
 * Performs exponentiation.
 */

Dual.prototype.pow = function (that) {
    that = new Dual(that);

    var b = this,
        x = that;

    var logb = this.ln();

    var result = new Dual(0);

    for (var i = 0; i < 100; i++) {
        var t1 = new Dual(1 / fac_rec(i));
        var t2 = pow(x, i);
        var t3 = pow(logb, i);
        result = result.add(t1.mul(t2).mul(t3));
    }

    return result;
}

/**
 * Computes the logarithm of a dual number with the supplied base.
 */
Dual.prototype.log = function (that) {
    that = new Dual(that)
    return this.ln().div(that.ln());
}

/**
 * Performs a comparison between two dual numbers using alphabetical ordering. 
 * The output is -1 if this<that, 0 if this=that, 1 otherwise.
 */

Dual.prototype.compareTo = function (that) {
    if (this.a < that.a) {
        return -1;
    } else if (this.a === that.a) {
        if (this.b < that.b) {
            return -1;
        } else if (this.b === that.b) {
            return 0;
        } else {
            return 1;
        }
    } else {
        return 1;
    }
}


Dual.prototype.toString = function () {
    return [
        (this.a === 0 ? "" : this.a + (Math.sign(this.b) === -1 ? "-" : "+")),
        Math.abs(this.b),
        eps
    ].join("");
}



//Aliases
Dual.prototype.plus = Dual.prototype.add;
Dual.prototype.subtract = Dual.prototype.sub;
Dual.prototype.minus = Dual.prototype.sub;
Dual.prototype.multiply = Dual.prototype.mul;
Dual.prototype.times = Dual.prototype.mul;

module.exports = Dual;