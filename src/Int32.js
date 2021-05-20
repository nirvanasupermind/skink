//Skink source code
//Usage permitted under terms of MIT License
"use strict";

function Int32(v = 0) {
    if (v instanceof Buffer) {
        this.buffer = v;
    } else {
        v = parseInt(v, 10);
        if (v < 0) {
            v += 4294967296;
        }

        this.buffer = Buffer.from([
            Math.trunc(v / 16777216) % 256,
            Math.trunc(v / 65536) % 256,
            Math.trunc(v / 256) % 256,
            v % 256
        ]);
    }
}

Int32.prototype.add = function (other) {
    if (!(other instanceof Int32))
        other = new Int32(other);

    if (this.toNumber() === 0 && other.toNumber() === 0)
        return new Int32(0);

    var x = this.buffer.slice(), y = other.buffer.slice();

    //x = [0, 0, 0, 255], y = [0, 0, 0, 2]
    //result = [0, 0, 1, 1] = 1 * 256 + 1 = 257
    var result = Buffer.alloc(x.length);
    var carry = 0;

    for (var i = x.length - 1; i >= 0; i--) {
        var a = x[i], b = y[i];

        var sum = a + b + carry;
        carry = Math.trunc(sum / 256);

        result[i] = sum % 256;
    }


    return new Int32(result);
}

Int32.prototype.neg = function () {
    return new Int32(this.buffer.map((byte) => 255 - byte)).add(1);
}


Int32.prototype.sub = function (other) {
    if (!(other instanceof Int32))
        other = new Int32(other);

    return this.add(other.neg());
}

Int32.prototype.mul = function (other) {
    if (!(other instanceof Int32))
        other = new Int32(other);

    if (this.toNumber() === 0 || other.toNumber() === 0)
        return new Int32(0);

    var x = this.buffer.slice(), y = other.buffer.slice();
    // will keep the result number in vector
    // in reverse order

    var result = Buffer.alloc(x.length);
    var a1 = x[0],
        b1 = x[1],
        c1 = x[2],
        d1 = x[3],
        a2 = y[0],
        b2 = y[1],
        c2 = y[2],
        d2 = y[3];
        
    //manual
    result[0] = (b2 * c1 + b1 * c2 + a2 * d1 + a1 * d2) % 256;
    result[1] = c1 * c2 + b2 * d1 + b1 * d2;
    result[2] = c2 * d1 + c1 * d2;
    result[3] = d1 * d2;

    for(var i = 1; i < result.length; i++) {
        if(result[i] >= 256) {
            var tmp = result[i];
            result[i - 1] += Math.trunc(tmp / 256);
            result[i] = tmp % 256;
        }
    }

    return new Int32(result);
}

Int32.prototype.div = function (other) {
    if (!(other instanceof Int32))
        other = new Int32(other);


    if (this.toNumber() === 0)
        return new Int32(0);

    var n = this.buffer, d = other.toNumber();
    var num = n,
        numLength = num.length,
        remainder = 0,
        answer = Buffer.alloc(numLength),
        i = 0;

    while(i < numLength){
        var digit = i < numLength ? num[i] : 0;


        answer[i] = Math.floor((digit + (remainder * 256))/d);
        remainder = (digit + (remainder * 256))%d;
        i++;
    }

    if(answer[answer.length - 1] < 0) {
        return new Int32(Buffer.from([...answer].map((byte) => -byte))).neg();
    } else {
    return new Int32(answer);
    }
}

Int32.prototype.and = function (other) {
   if(!(other instanceof Int32))
        other = new Int32(other);

   var result = Buffer.alloc(4);
   result[0] = this.buffer[0] & other.buffer[0];
   result[1] = this.buffer[1] & other.buffer[1]; 
   result[2] = this.buffer[2] & other.buffer[2]; 
   result[3] = this.buffer[3] & other.buffer[3];  

   return result;
}

Int32.prototype.or = function (other) {
    if(!(other instanceof Int32))
         other = new Int32(other);
 
    var result = Buffer.alloc(4);
    result[0] = this.buffer[0] | other.buffer[0];
    result[1] = this.buffer[1] | other.buffer[1]; 
    result[2] = this.buffer[2] | other.buffer[2]; 
    result[3] = this.buffer[3] | other.buffer[3];  
 
    return result;
 }

 
Int32.prototype.cmp = function (other) {
    if (!(other instanceof Int32))
        other = new Int32(other);
    return this.toNumber() < other.toNumber() ? -1
        : (this.toNumber() === other.toNumber() ? 0 : 1);
}

Int32.prototype.toNumber = function () {
    return this.buffer.readInt32BE();
}

Int32.prototype.toString = function (radix=10) {
    return this.toNumber().toString(radix);
}

module.exports = Int32;
