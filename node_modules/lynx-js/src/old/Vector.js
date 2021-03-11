/**
 * Creates a vector from an array.
 * @param {number[]} value 
 */
function Vector(value) {
    if (!(this instanceof Vector)) {
        return new Vector(value);
    } else if (value instanceof Vector) {
        Object.assign(this, value);
    } else {
        this.value = value.map(parseFloat);
    }
}

/**
 * Returns the size of a vector.
 */
Vector.prototype.size = function () {
    return this.value.length;
}

/**
 * Adds two vectors by element.
 */
Vector.prototype.add = function (that) {
    that = new Vector(that);
    if (this.size() !== that.size()) {
        throw new Error("Vector.prototype.add: Expecting vectors with the same size")
    }
    var result = this.value.map((num, index) => num + that.value[index]) //Add to each element
    return new Vector(result);
}


/**
 * Adds a vector and a scalar.
 */
Vector.prototype.adds = function (that) {
    var result = this.value.map((num) => num + that);
    return new Vector(result);
}


/**
 * Subtracts two vectors by element.
 */
Vector.prototype.sub = function (that) {
    that = new Vector(that);

    if (this.size() !== that.size()) {
        throw new Error("Vector.prototype.sub: Expecting vectors with the same size")
    }
    var result = this.value.map((num, index) => num - that.value[index]) //Add to each element
    return new Vector(result);
}


/**
 * Subtracts a vector and a scalar.
 */
Vector.prototype.subs = function (that) {
    var result = this.value.map((num) => num + that);
    return new Vector(result);
}


/**
 * Multiplies two vectors by element.
 */
Vector.prototype.mul = function (that) {
    that = new Vector(that);

    if (this.size() !== that.size()) {
        throw new Error("Vector.prototype.mul: Expecting vectors with the same size")
    }
    var result = this.value.map((num, index) => num * that.value[index]) //Add to each element
    return new Vector(result);
}





/**
 * Multiplies a vector and a scalar.
 */
Vector.prototype.muls = function (that) {
    var result = this.value.map((num) => num * that);
    return new Vector(result);
}


/**
 * Divides two vectors by element.
 */
Vector.prototype.div = function (that) {
    if (this.size() !== that.size()) {
        throw new Error("Vector.prototype.div: Expecting vectors with the same size")
    }
    var result = this.value.map((num, index) => num * that.value[index]) //Add to each element
    return new Vector(result);
}

/**
 * Divides a vector and a scalar.
 */
Vector.prototype.divs = function (that) {
    var result = this.value.map((num) => num / that);
    return new Vector(result);
}


/**
 * Computes the dot product of two vectors
 */
Vector.prototype.dot = function (that) {
    if (this.size() !== that.size()) {
        throw new Error("Vector.prototype.dot: Expecting vectors with the same size")
    }

    return this.mul(that).value.reduce((acc, no) => acc + no);
}

/**
 * Computes the norm of a vector
 */
Vector.prototype.norm = function () {
    var result = this.value.map((e) => Math.pow(Math.abs(e), this.size())).reduce((acc, no) => acc + no);
    result = Math.pow(result, 1 / this.size());
    return result;
}


Vector.prototype.toString = function () {
    return "vector("+JSON.stringify(this.value)+")";
}

//Aliases
Vector.prototype.plus = Vector.prototype.add;
Vector.prototype.subtract = Vector.prototype.sub;
Vector.prototype.minus = Vector.prototype.sub;
Vector.prototype.multiply = Vector.prototype.mul;
Vector.prototype.times = Vector.prototype.mul;

module.exports = Vector;