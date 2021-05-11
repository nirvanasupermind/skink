//nightjar Library
//Usage permitted under terms of MIT License
function createInt(bits) {
    //HELPERS
    var and = (a, b) => a && b;
    var or = (a, b) => a || b;
    var xor = (a, b) => a !== b;
    //taken from https://stackoverflow.com/questions/40353000/javascript-add-two-binary-numbers-returning-binary
    function halfAdder(a, b) {
        const sum = xor(a, b);
        const carry = and(a, b);
        return [sum, carry];
    }

    function fullAdder(a, b, carry) {
        halfAdd = halfAdder(a, b);
        const sum = xor(carry, halfAdd[0]);
        carry = and(carry, halfAdd[0]);
        carry = or(carry, halfAdd[1]);
        return [sum, carry];
    }


    //taken from https://codereview.stackexchange.com/questions/92966/multiplying-and-adding-big-numbers-represented-with-strings
    function add(a, b) {
        if (parseInt(a) == 0 && parseInt(b) == 0) {
            return "0";
        }

        a = a.split("").reverse();
        b = b.split("").reverse();
        var result = [];

        for (var i = 0; (a[i] >= 0) || (b[i] >= 0); i++) {
            var sum = (parseInt(a[i]) || 0) + (parseInt(b[i]) || 0);

            if (!result[i]) {
                result[i] = 0;
            }

            var next = parseInt((result[i] + sum) / 10);
            result[i] = (result[i] + sum) % 10;

            if (next) {
                result[i + 1] = next;
            }
        }

        return result.reverse().join("");
    }

    //taken from https://stackoverflow.com/questions/2050111/subtracting-long-numbers-in-javascript
    var subtract = (a, b) => [a, b].map(n => [...n].reverse()).reduce((a, b) => a.reduce((r, d, i) => {
        let s = d - (b[i] || 0)
        if (s < 0) {
            s += 10
            a[i + 1]--
        }
        return '' + s + r
    }, '').replace(/^0+/, ''))


    //taken from https://codereview.stackexchange.com/questions/92966/multiplying-and-adding-big-numbers-represented-with-strings
    function multiply(a, b) {
        if (parseInt(a) === 0 || parseInt(b) === 0) {
            return "0";
        }

        a = a.split("").reverse();
        b = b.split("").reverse();
        var result = [];

        for (var i = 0; a[i] >= 0; i++) {
            for (var j = 0; b[j] >= 0; j++) {
                if (!result[i + j]) {
                    result[i + j] = 0;
                }

                result[i + j] += a[i] * b[j];
            }
        }

        for (var i = 0; result[i] >= 0; i++) {
            if (result[i] >= 10) {
                if (!result[i + 1]) {
                    result[i + 1] = 0;
                }

                result[i + 1] += parseInt(result[i] / 10);
                result[i] %= 10;
            }
        }

        return result.reverse().join("");
    }

    function factorial(n) {
        if ((n === 0) || (n === 1))
            return 1;
        else
            return (n * factorial(n - 1));
    }


    //taken from https://locutus.io/php/strings/ord/
    function ord(string) {
        const str = string + ''
        const code = str.charCodeAt(0)
        if (code >= 0xD800 && code <= 0xDBFF) {
            // High surrogate (could change last hex to 0xDB7F to treat
            // high private surrogates as single characters)
            const hi = code
            if (str.length === 1) {
                // This is just a high surrogate with no following low surrogate,
                // so we return its value;
                return code
                // we could also throw an error as it is not a complete character,
                // but someone may want to know
            }
            const low = str.charCodeAt(1)
            return ((hi - 0xD800) * 0x400) + (low - 0xDC00) + 0x10000
        }
        if (code >= 0xDC00 && code <= 0xDFFF) {
            // Low surrogate
            // This is just a low surrogate with no preceding high surrogate,
            // so we return its value;
            return code
            // we could also throw an error as it is not a complete character,
            // but someone may want to know
        }
        return code
    }

    function addDigits(a, b, c = null) {
        if (c === null) {
            return [a && b, a !== b]
        } else {
            var sum1 = addDigits(a, b)
            var sum2 = addDigits(sum1[sum1.length - 1], c)
            return (sum1.count === 1) ? sum2 : ((sum2.count === 1) ? [sum1[0]].concat(sum2) : [sum1[0]])
        }
    }

    // Returns true if str1 is smaller than str2.
    function isSmaller(str1, str2) {
        // Calculate lengths of both string
        var n1 = str1.length, n2 = str2.length;
        if (n1 < n2)
            return true;
        if (n2 < n1)
            return false;

        for (var i = 0; i < n1; i++)
            if (str1.charAt(i) < str2.charAt(i))
                return true;
            else if (str1.charAt(i) > str2.charAt(i))
                return false;

        return false;
    }



    function longDivision(number, divisor) {
        if (isSmaller(number, divisor.toString())) { return "0"; }
        //As result can be very large store it in string  
        var ans = "";
        //Find prefix of number that is larger than divisor.  
        var idx = 0;
        var temp = ord(number[idx]) - ord('0');
        while (temp < divisor) {
            temp = (temp * 10 + ord(number[idx + 1]) - ord('0'));
            idx += 1;
        }
        idx += 1;

        //Repeatedly divide divisor with temp. After every division, update temp to 
        //include one more digit.  
        while (number.length > idx) {
            //Store result in answer i.e. temp / divisor  
            ans += String.fromCharCode((temp / divisor) + ord('0'));
            //Take next digit of number 
            temp = ((temp % divisor) * 10 + ord(number[idx]) - ord('0'));
            idx += 1;
        }

        ans += String.fromCharCode((temp / divisor) + ord('0'));

        //If divisor is greater than number  
        if (ans.length === 0) {
            return "0";
        }
        //else return ans  
        return ans;
    }

    function mod(a, b) {
        return subtract(a, multiply(longDivision(a, b), b)) || "0";
    }

    function pow(a, b) {
        return (b === 0 ? "1" : multiply(pow(a, b - 1), a));
    }

    function from_v(v) {
        var result = Object.create(BaseInt.prototype);
        result.v = v.slice(-bits);
        return result;
    }

    //Converts number to hex
    function toBinary(v) {
        var result = new Array(bits - 1);
        for (var i = bits - 1; i >= 0; i--) {
            result[i] = parseInt(mod(v, "2"));
            if (parseInt(v) < 2) {
                v = "0";
            } else {
                v = longDivision(v, "2");
            }
        }

        return result.map((e) => !!e);
    }

    //MAIN CLASS
    function BaseInt(v = "0") {
        if (!(this instanceof BaseInt)) {
            return new BaseInt(v);
        } else {
            if (v instanceof BaseInt) {
                Object.assign(this, v);
                this.bits = bits;
            } else {
                v = "" + v;
                if (v.charAt(0) === "-")
                    v = subtract(pow("2", bits), v.substring(1));
                this.v = toBinary("" + v);
                this.bits = bits;
            }
        }
    }

    /**
     * Addition.
     * @param {string|number|BaseInt} other 
     */
    BaseInt.prototype.add = function (other) {
        other = new BaseInt(other);

        var a = this.v, b = other.v;
        let sum = [];
        let carry = '';

        for (var i = a.length - 1; i >= 0; i--) {
            if (i == a.length - 1) {
                //half add the first pair
                const halfAdd1 = halfAdder(a[i], b[i]);
                sum.unshift(halfAdd1[0]);
                carry = halfAdd1[1];
            } else {
                //full add the rest
                const fullAdd = fullAdder(a[i], b[i], carry);
                sum.unshift(fullAdd[0]);
                carry = fullAdd[1];
            }
        }

        return from_v(sum);
    }

    /**
     * Returns whether number is negative.
     */
    BaseInt.prototype.isNegative = function () {
        return !!this.v[0];
    }

    /**
     * Returns whether number is positive.
     */
    BaseInt.prototype.isPositive = function () {
        return !this.v[0];
    }

    /**
     * Returns the negated value.
     */
    BaseInt.prototype.neg = function () {
        return from_v(this.v.map((bit) => !bit)).add(1);
    }

    /**
     * Subtraction.
     * @param {string|number|BaseInt} other 
     */
    BaseInt.prototype.sub = function (other) {
        other = new BaseInt(other);
        return this.add(other.neg());
    }

    /**
     * Multiplication.
     * @param {string|number|BaseInt} other 
     */
    BaseInt.prototype.mul = function (other) {
        other = new BaseInt(other);

        if (this.toNumber() === 0 || other.toNumber() === 0) return new BaseInt(0);
        if (this.isNegative() && other.isPositive()) return this.neg().mul(other).neg();
        if (this.isNegative() && other.isNegative()) return this.neg().mul(other.neg());
        if (this.isPositive() && other.isNegative()) return this.mul(other.neg()).neg();

        var a = this.v.reverse().map(Number), b = other.v.reverse().map(Number);

        var result = [];

        for (var i = 0; a[i] >= 0; i++) {
            for (var j = 0; b[j] >= 0; j++) {
                if (!result[i + j]) {
                    result[i + j] = 0;
                }

                result[i + j] += a[i] * b[j];
            }
        }

        for (var i = 0; result[i] >= 0; i++) {
            if (result[i] >= 2) {
                if (!result[i + 1]) {
                    result[i + 1] = 0;
                }

                result[i + 1] += parseInt(result[i] / 2);
                result[i] %= 2;
            }
        }

        return from_v(result.reverse().map(Boolean));
    }

    /**
     * Truncated division.
     * @param {string|number|BaseInt} other 
     */
    BaseInt.prototype.div = function (other) {
        other = new BaseInt(other);

        if (this.toNumber() === 0 || other.toNumber() === 0) return new BaseInt(0);
        if (this.isNegative() && other.isPositive()) return this.neg().div(other).neg();
        if (this.isNegative() && other.isNegative()) return this.neg().div(other.neg());
        if (this.isPositive() && other.isNegative()) return this.div(other.neg()).neg();

        var num = this.v,
            numLength = num.length,
            remainder = 0,
            answer = [],
            d = other.toNumber();
        i = 0;

        while (i < numLength) {
            var digit = Number(num[i]);

            answer.push(Math.floor((digit + (remainder * 2)) / d));
            remainder = (digit + (remainder * 2)) % d;
            i++;
        }

        return from_v(answer.map(Boolean));
    }

    /**
     * Returns the division remainder.
     * @param {BaseInt} other 
     */
    BaseInt.prototype.mod = function (other) {
        return this.sub(this.div(other).mul(other));
    }

    /**
     * Returns the bitwise NOT.
     */
    BaseInt.prototype.not = function () {
        return from_v(this.v.map((el) => !el));
    }

    /**
     * Returns the bitwise AND.
     * @param {string|number|BaseInt} other
     */
    BaseInt.prototype.and = function (other) {
        other = new BaseInt(other);
        return from_v(this.v.map((el,i) => el && other.v[i]));
    }


    /**
     * Returns the bitwise OR.
     * @param {string|number|BaseInt} other
     */
    BaseInt.prototype.or = function (other) {
        other = new BaseInt(other);
        return from_v(this.v.map((el,i) => el || other.v[i]));
    }

    /**
     * Returns the bitwise XOR.
     * @param {string|number|BaseInt} other
     */
    BaseInt.prototype.xor = function (other) {
        other = new BaseInt(other);
        return from_v(this.v.map((el,i) => !el ^ !other.v[i]));
    }

    //Alias
    BaseInt.prototype.plus = BaseInt.prototype.add;
    BaseInt.prototype.negate = BaseInt.prototype.neg;
    BaseInt.prototype.absoluteValue = BaseInt.prototype.abs;
    BaseInt.prototype.minus = BaseInt.prototype.subtract = BaseInt.prototype.sub;
    BaseInt.prototype.multiply = BaseInt.prototype.times = BaseInt.prototype.mul;
    BaseInt.prototype.divide = BaseInt.prototype.div;
    BaseInt.prototype.modular = BaseInt.prototype.mod;


    /**
     * Converts the number into Number.
     */
    BaseInt.prototype.toNumber = function () {
        if (this.isNegative()) return -(this.neg().toNumber());
        var result = 0;
        for (var i = 0; i < this.v.length; i++) {
            if (this.v[i]) result += Math.pow(2, this.v.length - i - 1);
        }

        return result;
    }


    /**
     * Converts the number into String.
     */
    BaseInt.prototype.toString = function () {
        if (this.v[0] && this.v.slice(1).every((n) => !n))
            return "-" + pow("2", bits - 1)
        if (this.isNegative()) return "-" + this.neg();
        var result = "0";
        for (var i = 0; i < this.v.length; i++) {
            if (this.v[i]) result = add(result, pow("2", this.v.length - i - 1));
        }

        return result;
    }

    BaseInt.MIN_VALUE = new BaseInt(add(pow("2", bits - 1), "1"));
    BaseInt.MAX_VALUE = new BaseInt(subtract(pow("2", bits - 1), "1"));

    return BaseInt;
}


module.exports = {
    "Int32": createInt(32),
    "Int64": createInt(64),
    "createInt": createInt
}