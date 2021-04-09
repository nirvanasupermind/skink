//helper functions
//BigInt +,*
function multiply(a, b) {
  if ((parseInt(a)) == 0 || (parseInt(b)) == 0) {
    return '0';
  }

  a = a.split('').reverse();
  b = b.split('').reverse();
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

  return result.reverse().join('');
}

function add(a, b) {
  if ((parseInt(a)) == 0 && (parseInt(b)) == 0) {
    return '0';
  }

  a = a.split('').reverse();
  b = b.split('').reverse();
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

  return result.reverse().join('');
}

// Returns '0' for '1' and '1' for '0'
function flip(c) {
  return (c == '0') ? '1' : '0';
}

// Print 1's and 2's complement of binary number
// represented by "bin"
function findTwoscomplement(bin) {
  var n = bin.length;
  var i;

  var ones = "", twos = "";
  ones = twos = "";

  // for ones complement flip every bit
  for (i = 0; i < n; i++) {
    ones += flip(bin.charAt(i));
  }

  // for two's complement go from right to left in
  // ones complement and if we get 1 make, we make
  // them 0 and keep going left when we get first
  // 0, make that 1 and go out of loop
  twos = ones;
  for (i = n - 1; i >= 0; i--) {
    if (ones.charAt(i) == '1') {
      twos = twos.substring(0, i) + '0' + twos.substring(i + 1);
    }
    else {
      twos = twos.substring(0, i) + '1' + twos.substring(i + 1);
      break;
    }
  }

  // If No break : all are 1 as in 111 or 11111;
  // in such case, add extra 1 at beginning
  if (i == -1) {
    twos = '1' + twos;
  }

  return twos;
}

/**
 * String.padStart()
 * version 1.0.1
 * Feature	        Chrome  Firefox Internet Explorer   Opera	Safari	Edge
 * Basic support	57   	51      (No)	            44   	10      15
 * -------------------------------------------------------------------------------
 */
if (!String.prototype.padStart) {
  String.prototype.padStart = function padStart(targetLength, padString) {
    targetLength = targetLength >> 0; //floor if number or convert non-number to 0;
    padString = String(typeof padString !== 'undefined' ? padString : ' ');
    if (this.length > targetLength) {
      return String(this);
    } else {
      targetLength = targetLength - this.length;
      if (targetLength > padString.length) {
        padString += padString.repeat(targetLength / padString.length); //append to original to ensure we are longer than needed
      }
      return padString.slice(0, targetLength) + String(this);
    }
  };
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
    if (str1[i] < str2[i])
      return true;
    else if (str1[i] > str2[i])
      return false;

  return false;
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

function longDivision(number, divisor) {
  if (isSmaller(number, "" + divisor)) {
    return "0";
  } else {
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
}


// Function to compute num (mod a)
function mod(num, a) {
  // Initialize result
  var res = 0;

  // One by one process all digits of 'num'
  for (var i = 0; i < num.length; i++)
    res = (res * 10 + Number(num.charAt(i))) % a;

  return "" + res;
}


function bitLength(value) {
  if (isSmaller(value, "2"))
    return 1;
  var result = 0;
  while (isSmaller("0", value)) {
    result++;
    value = longDivision(value, 2);
  }


  return result;
}

function toBinary(value) {
  var result = "";
  var temp = value;
  var numDigits = bitLength(value);

  //Convert using remainders.
  for (var i = 0; i < numDigits; i++) {
    var t1 = temp;
    temp = longDivision(t1, 2);
    result = mod(t1, 2) + result;
  }

  return result;
}


module.exports = (bits) => {
  /**
   * An integer with specified number of bits.
   */
  class GenericInt {
    /**
     * The constructor for GenericInt.
     */
    constructor(value = "0", isBinary = false) {
      if (value instanceof GenericInt) {
        Object.assign(this, value);
      } else if (isBinary) {
        this.value = ("" + value).slice(-bits).padStart(bits, "0");
      } else {
        value = "" + value;
        if (value.charAt(0) === "-") {
          //two's complement
          if (+value === -1) {
            this.value = "1".repeat(bits);
          } else {
            this.value = findTwoscomplement(toBinary(value.substring(1)).padStart(bits, "0").slice(-bits));
          }
        } else {
          this.value = toBinary(value)
            .slice(-bits)
            .padStart(bits, "0");
        }
      }
    }

    /**
     * Returns whether number is negative.
     */
    isNeg() {
      return this.value.charAt(0) === "1";
    }

    /**
     * Returns the negated value.
     */
    neg() {
      if (Number(this.value) === 1) {
        return new GenericInt(-1);
      } else {
        return new GenericInt(findTwoscomplement(this.value), true);
      }
    }

    /**
     * Addition.
     */
    add(that) {
      that = new GenericInt(that);
      var a = this.value;
      var b = that.value;

      var longer = a.length > b.length ? a : b;
      var shorter = a.length > b.length ? b : a;

      while (shorter.length < longer.length)
        shorter = "0" + shorter;

      a = longer;
      b = shorter;

      var carry = '0';
      var sum = "";
      for (var i = 0; i < a.length; i++) {
        var place = a.length - i - 1;
        var digisum = [a.charAt(place), b.charAt(place), carry].reduce((A, B) => (A * 1) + (B * 1)).toString(2);
        if (digisum.length != 1)
          carry = digisum.charAt(0);
        else
          carry = '0';
        sum = digisum.charAt(digisum.length - 1) + sum;
      }

      sum = carry + sum;

      return new GenericInt(sum, true);
    }

    /**
     * Subtraction.
     */
    sub(that) {
      that = new GenericInt(that);
      return this.add(that.neg());
    }

    /**
     * Multiplication.
     */
    mul(that) {
      that = new GenericInt(that);
      if (this.isNeg() && that.isNeg()) {
        return this.neg().mul(that.neg())
      } else if (this.isNeg() && !that.isNeg()) {
        return this.neg().mul(that).neg();
      } else if (!this.isNeg() && that.isNeg()) {
        return this.mul(that.neg()).neg();
      } else {
        return new GenericInt(multiply(this.toString(), that.toString()));
      }
    }

    /**
     * Division.
     */
    div(that) {
      that = new GenericInt(that);
      if (this.isNeg() && that.isNeg()) {
        return this.neg().div(that.neg())
      } else if (this.isNeg() && !that.isNeg()) {
        return this.neg().div(that).neg();
      } else if (!this.isNeg() && that.isNeg()) {
        return this.div(that.neg()).neg();
      } else {
        return new GenericInt(longDivision(this.toString(), that.toString() * 1));
      }
    }


    compareTo(that) {
      that = new GenericInt(that);
      if (this.isNeg() && that.isNeg()) {
        return -this.neg().compareTo(that.neg());
      } else if (this.isNeg() && !that.isNeg()) {
        return -1;
      } else if (!this.isNeg() && that.isNeg()) {
        return this.div(that.neg()).neg();
      } else if (this.value === that.value) {
        return 0;
      } else if (isSmaller(this.value, that.value)) {
        return -1;
      } else {
        return 1;
      }
    }

    toNumber() {
      return +this.toString();
    }


    toString() {
      if (this.isNeg())
        return "-" + this.neg().toString();
      //Q&D implementation of BigInt power
      let pow = (a, b) => b === 0 ? "1" : multiply(pow(a, b - 1), a);
      var result = "0";
      //Reverse this.value
      var reversedValue = this.value.split("").reverse().join("");
      for (var i = 0; i < reversedValue.length; i++) {
        if (reversedValue.charAt(i) === "1") {
          //Only update result if the current bit is 1.
          result = add(result, pow("2", i));
        }
      }

      return result;


    }
  }

  return GenericInt;
}

