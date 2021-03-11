/**
 * Stores integral numbers of arbitrary size.
 * @param {*} val 
 */
function FatInt(val = "0", s) {
    if (!(this instanceof FatInt)) {
        return new FatInt(val);
    }

    val = String(val)
    var temp = val;
    if (val.charAt(0) === "-") {
        //Deal with negatives
        val = val.substr(1);
    }


    var i = 0;
    while (val.charAt(i) == '0')
        i++;

    this.value = val.substring(i);
    this.s = (s == null ? Math.sign(parseFloat(temp)) > 0 : s);
}

//Utility function to add numbers
function addDigits() {
    var vargv = [].slice.call(arguments);
    return vargv.reduce((a, b) => (parseFloat(a) + parseFloat(b)).toString());
}


//Utility function to sub numbers
function subDigits() {
    var vargv = [].slice.call(arguments);
    return vargv.reduce((a, b) => (parseFloat(a) - parseFloat(b)).toString());
}

/**
 * Addition
 */
FatInt.prototype.add = function (that) {
    var x = this, y = that;
    if (!this.s && that.s) { // Deal with negative quantities.
        return that.sub(this.neg());
    } else if (this.s && !that.s) {
        return this.sub(that.neg());
    } else if (!this.s && !that.s) {
        return this.neg().add(that.neg()).neg();
    } else {
        // Now it's our main body...
        //  It is assumed X and Y are both +ve
        //  Because we've filtered the rest ;)
        var a = this.value;
        var b = that.value;

        var longer = a.length > b.length ? a : b;
        var shorter = a.length > b.length ? b : a;

        while (shorter.length < longer.length)
            shorter = 0 + shorter;

        a = longer;
        b = shorter;

        var carry = '0';
        var sum = "";
        for (var i = 0; i < a.length; i++) {
            var place = a.length - i - 1;
            var digisum = addDigits(a.charAt(place), b.charAt(place), carry);
            if (digisum.length != 1)
                carry = digisum.charAt(0);
            else
                carry = '0';
            sum = digisum.charAt(digisum.length - 1) + sum;
        }
        sum = carry + sum;
        return new FatInt(sum);
    }
}

/**
 * Negation
 */
FatInt.prototype.neg = function () {
    return new FatInt(this.value, !this.s);
}

// Returns true if str1 is smaller than str2.
function isSmaller(str1, str2) {
    // Calculate lengths of both string
    var n1 = str1.length(), n2 = str2.length();

    if (n1 < n2)
        return true;
    if (n2 < n1)
        return false;

    for (var i = 0; i < n1; i++)
        if (str1[i] < str2[i])
            return true;
        else if (str1[i] > str2[i])
            return false;

    return false;
}

/**
 * Subtraction
 */
FatInt.prototype.sub = function (that) {
    var a = this.value;
    var b = that.value;

    var longer = a.length > b.length ? a : b;
    var shorter = a.length > b.length ? b : a;

    while (shorter.length < longer.length)
        shorter = 0 + shorter;

    a = longer;
    b = shorter;

    var [number1, number2] = [a, b];
    var carry = 0;
    var result = [];
    for (var i = number1.length - 1; i >= 0; i--) {
        var newDigit = parseFloat(number1[i]) - parseFloat(number2[i]) + carry;
        if (newDigit >= 10) {
            carry = 1;
            newDigit -= 10;
        } else if (newDigit < 0) {
            carry = -1;
            newDigit += 10;
        } else {
            carry = 0;
        }
        result[i] = newDigit;
    }
    while (result[0] === 0) {
        result.shift();
    }
    return new FatInt(result.join(""));
}

/**
 * Convert to native number
 */
FatInt.prototype.toDouble = function () {
    return parseFloat(this.value) * this.s;
}

/**
 * Performs a comparison between two numbers. If the numbers are equal, it returns 0. If the first number is greater, it returns 1. If the first number is lesser, it returns -1.
 */
FatInt.prototype.compareTo = function (that) {
    if (!this.s && that.s) {
        return -1;
    } else if (this.s && !that.s) {
        return 1;
    } else if (!this.s && !that.s) {
    } else {
        // Now it's our main body...
        //  It is assumed X and Y are both +ve
        //  Because we've filtered the rest ;)
        if (isSmaller(this.value, that.value)) {
            return -1;
        } else if(this.value === that.value) {
            return 0;
        } else {
            return 1;
        }
    }
}

FatInt.prototype.toString = function () {
    return (this.s ? "" : "-") + this.value;
}

module.exports = FatInt;