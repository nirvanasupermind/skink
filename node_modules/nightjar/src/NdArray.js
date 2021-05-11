var assert = require("assert");
const { on } = require("events");
var MAX = 30;
var tmp = 3;
//HELPERS
Object.defineProperty(Array.prototype, 'eachConsecutive', {
    value: function (n) {
        var copy = this.concat(), result = [];
        while (copy.length) result.push(copy.splice(0, n));
        return result;
    }
});

//taken from https://stackoverflow.com/questions/17895039/how-to-insert-line-break-after-every-80-characters/17895095
function textFold(input, lineSize) {
    const output = []
    let outputCharCount = 0
    let outputCharsInCurrentLine = 0
    for (var i = 0; i < input.length; i++) {
      const inputChar = input[i]
      output[outputCharCount++] = inputChar
      if (inputChar === '\n') {
        outputCharsInCurrentLine = 0
      } else if (outputCharsInCurrentLine > lineSize-2) {
        output[outputCharCount++] = '\n  '
        outputCharsInCurrentLine = 0
      } else {
        outputCharsInCurrentLine++
      }
    }
    
    return output.join('')
  }


Array.prototype.eq = function (that) { return JSON.stringify(this) === JSON.stringify(that); }
Array.prototype.ne = function (that) { return !this.eq(that); }

function parseInteger(v) {
    return Math.trunc(parseFloat(v));
}

//taken from https://www.techiedelight.com/recursively-flatten-nested-array-javascript/
function flatten(arr) {
    return arr.reduce((acc, cur) => acc.concat(Array.isArray(cur) ? flatten(cur) : cur), []);
};

//taken from https://stackoverflow.com/questions/55420156/get-arrays-depth-in-javascript
function getArrayDepth(value) {
    return Array.isArray(value) ?
        1 + Math.max(...value.map(getArrayDepth)) :
        0;
}

function neg_index(a, b) {
    if (b >= 0) return b;
    return a + b;
}

// pre: a !== b, each item is a scalar
function array_equals(a, b) {
    return a.length === b.length && a.every(function (value, index) {
        return value === b[index];
    });
};

//taken from http://stackoverflow.com/questions/13814621/how-can-i-get-the-dimensions-of-a-multidimensional-javascript-array/13832026#13832026
function getdim(arr) {
    if (/*!(arr instanceof Array) || */!arr.length) {
        return []; // current array has no dimension
    }
    var dim = arr.reduce(function (result, current) {
        // check each element of arr against the first element
        // to make sure it has the same dimensions
        return array_equals(result, getdim(current)) ? result : false;
    }, getdim(arr[0]));

    // dim is either false or an array
    return dim && [arr.length].concat(dim);
}


//element-wise binary operator
function bin_op(f, a, b) {
    assert(a.length === b.length);
    return a.map((_, i) => f(a[i], b[i]));
}

//taken from http://jsfiddle.net/kkf43/
function multiply(array) {
    var result = 1;
    for (var i = 0; i < array.length; i++) {
        result = result * array[i];
    }

    return result;
}

function indent(a, b) {
    return a.split("\n").map((e) => b + e).join("\n");
}

function toArray(v) {
    return [...v];
}


function printf(v) {
    if (v instanceof Array) v = new NdArray(v);
    var data = v.data, shape = v.shape;
    if (shape.length === 1) {
        if (data.length > MAX) {
            var t = printf(data.slice(0,MAX));
            return t.slice(0,-1) + "...}";
        } /* else if(data.length > MAX*2/3) {
            var result = "{\n";
            for(var i = 0; i < data.length; i++) {
                if(i === data.length-1) 
                    result += "  "+data[i].toFixed(prec).replace(/([0-9]+(\.[0-9]+[1-9])?)(\.?0+$)/,'$1')+"\n";
                else
                    result += "  "+data[i].toFixed(prec).replace(/([0-9]+(\.[0-9]+[1-9])?)(\.?0+$)/,'$1')+",\n";
            }

            result += "}";
            return result;
        } */ else {
            if(data.length < tmp*3) { return "{"+data.join(", ")+"}"; }
         var result = "{"+data.slice(0,tmp-1).join(", ");
         for(var i = tmp; i < data.length; i += tmp) {
             result += ",\n "+data.slice(i,i+tmp-1).join(", ");
         }

         result += "}";

         return result;
        }
    } else {
        var arr = v.toArray();
        if(arr.length === 1) return "{"+printf(arr[0])+"}";
        if(arr.length > MAX) return printf(arr.slice(0,MAX)).slice(0,-2)+",\n  ...\n}";
        var result = "{\n"+indent(printf(arr[0]), "  ");
        for(var i = 1; i < arr.length; i++) {
            var t = indent(printf(arr[i]), "  ");
            if(t.length > MAX*3) {
                result += ",\n\n"+indent(printf(arr[i]), "  ");
            } else {
            result += ",\n"+indent(printf(arr[i]), "  ");
            }
        }

        result += "\n}";
        return result;
    }
}

//MAIN CLASS
/**
 * An N-dimensional array object.
 * @param {Array} data 
 */
function NdArray(data, shape = null) {
    if (!(this instanceof NdArray)) {
        return new NdArray(data, shape);
    } /* else if (data instanceof NdArray) {
        this.data = data.data;
        this.shape = data.shape;
    } */ else {
        if (shape) {
            this.data = toArray(data).map(parseFloat);
            this.shape = toArray(shape).map(parseInteger);
            assert(multiply(this.shape) === data.length);
        } else {
            data = toArray(data);
            this.data = flatten(data);
            assert(getdim(data));
            this.shape = getdim(data);
        }
    }
}

NdArray.prototype[Symbol.iterator] = function* () {
    for (var i = 0; i < this.toArray().length; i++) {
        yield this.toArray()[i];
    }
}

/**
 * Returns the array with axes transposed.
 */
NdArray.prototype.transpose = function () {
return new NdArray(this.data, this.shape.reverse());
}

/**
 * Reverse the order of elements in an array.
 */
NdArray.prototype.flip = function () { 
    return new NdArray(this.data.reverse(), this.shape);
}

/**
 * Returns the sum of `this` and `other`, element-wise.
 * @param {Array|NdArray} other 
 */
NdArray.prototype.add = function (other) {
    other = new NdArray(other);
    return new NdArray(bin_op((a, b) => a + b, this.data, other.data), this.shape);
}

/**
 * Returns the difference of `this` and `other`, element-wise.
 * @param {Array|NdArray} other 
 */
NdArray.prototype.sub = function (other) {
    other = new NdArray(other);
    return new NdArray(bin_op((a, b) => a - b, this.data, other.data), this.shape);
}

/**
 * Returns the product of `this` and `other`, element-wise.
 * @param {Array|NdArray} other 
 */
NdArray.prototype.mul = function (other) {
    other = new NdArray(other);
    return new NdArray(bin_op((a, b) => a * b, this.data, other.data), this.shape);
}

/**
 * Returns the sine, element-wise.
 */
NdArray.prototype.sin = function () {
    return new NdArray(this.data.map(Math.sin), this.shape);
}

/**
 * Returns the cosine, element-wise.
 */
NdArray.prototype.cos = function () {
    return new NdArray(this.data.map(Math.cos), this.shape);
}

/**
 * Returns the tangent, element-wise.
 */
NdArray.prototype.tan = function () {
    return new NdArray(this.data.map(Math.tan), this.shape);
}


/**
 * Returns the inverse sine, element-wise.
 */
NdArray.prototype.asin = function () {
    return new NdArray(this.data.map(Math.asin), this.shape);
}

/**
 * Returns the inverse cosine, element-wise.
 */
NdArray.prototype.acos = function () {
    return new NdArray(this.data.map(Math.acos), this.shape);
}

/**
 * Returns the inverse tangent, element-wise.
 */
NdArray.prototype.atan = function () {
    return new NdArray(this.data.map(Math.atan), this.shape);
}

/**
 * Element-wise arc tangent of `this/other`.
 * @param {Array|NdArray} other 
 */
NdArray.prototype.atan2 = function (other) {
    other = new NdArray(other);
    return new NdArray(bin_op(Math.atan2, this.data, other.data), this.shape);
}

/**
 * Returns the exponential function, element-wise.
 */ 
NdArray.prototype.exp = function () {
    return new NdArray(this.data.map(Math.exp), this.shape);
}


/**
 * Returns the natural logarithm, element-wise.
 */ 
NdArray.prototype.log = function () {
    return new NdArray(this.data.map(Math.log), this.shape);
}


/**
 * Applies square root, element-wise.
 */ 
NdArray.prototype.sqrt = function () {
    return new NdArray(this.data.map(Math.sqrt), this.shape);
}

/**
 * First array elements raised to powers from second array, element-wise.
 * @param {Array|NdArray} other
 */
NdArray.prototype.pow = function (other) {
    other = new NdArray(other);
    return new NdArray(bin_op(Math.pow, this.data, other.data), this.shape); 
}


/**
 * Converts the array into Array.
 */
NdArray.prototype.toArray = function () {
    var result = this.data;
    for (var i = this.shape.length - 1; i >= 1; i--) {
        result = result.eachConsecutive(this.shape[i]);
    }

    return result;
}

/**
 * Retrieves a value from the array.
 * @param {...number} idx
 */
NdArray.prototype.get = function (...idx) {
    idx = idx.map(parseInteger);
    var result = this.toArray();
    for (var i = 0; i < idx.length; i++) {
        result = result[idx[i]];
    }

    if (Array.isArray(result)) {
        return new NdArray(result);
    } else {
        return result;
    }
}



/**
 * Converts the array into String.
 */
NdArray.prototype.toString = function () {
    return printf(this);
}


/**
 * Returns the product of `this` and `other`, element-wise.
 * @param {Array|NdArray} other 
 */
NdArray.prototype.mul = function (other) {
    other = new NdArray(other);
    return new NdArray(bin_op((a, b) => a * b, this.data, other.data), this.shape);
}

/**
 * Returns the scalar product of `this` and `other`.
 * @param {string|number} other 
 */
NdArray.prototype.scalar = function (other) {
    other = parseFloat(other);
    return new NdArray(this.data.map((el) => other*el), this.shape);
}



//Alias.
NdArray.prototype.plus = NdArray.prototype.add;
NdArray.prototype.minus = NdArray.prototype.subtract = NdArray.prototype.sub;
NdArray.prototype.multiply = NdArray.prototype.times = NdArray.prototype.mul;
NdArray.prototype.divide = NdArray.prototype.div;
NdArray.prototype.modular = NdArray.prototype.mod;
NdArray.prototype.arcsin = NdArray.prototype.asin;
NdArray.prototype.arccos = NdArray.prototype.acos;
NdArray.prototype.arctan = NdArray.prototype.atan;
NdArray.prototype.exponential = NdArray.prototype.exp;
NdArray.prototype.ln = NdArray.prototype.log;
NdArray.prototype.squareRoot = NdArray.prototype.sqrt;
NdArray.prototype.toPower = NdArray.prototype.power = NdArray.prototype.pow;

module.exports = NdArray;