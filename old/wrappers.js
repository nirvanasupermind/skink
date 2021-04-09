//In this module, we define the wrapper types. 
//We need to define the wrapper types since JS objects 
//aren't compatible with our storage system.
var Environment = require("./Environment.js");
var Int32 = require("./GenericInt.js")(32);
var Int64 = require("./GenericInt.js")(64);

module.exports = new function () {
    var E = () => new Environment();
    var wrappers = this;

    var falsey = [
        new Int32(0),
        new Int64(0),
        0,
        false
    ].map(JSON.stringify);

    //Int32 wrapper
    this.int = new Environment({
        constructor(self, value) {
            self.parent = wrappers.int;
            if (value instanceof Environment && value.has("value")) {
                value = value.lookup("value");
            }

            //Define the basic value.
            self.define("value", new Int32(value));
            //Addition
            self.define("add", function (that) {
                return wrappers.int.lookup("constructor")(E(), self.lookup("value").add(that.lookup("value")));
            })
            //Subtraction
            self.define("sub", function (that) {
                return wrappers.int.lookup("constructor")(E(), self.lookup("value").sub(that.lookup("value")));
            })
            //Multiplication
            self.define("mul", function (that) {
                return wrappers.int.lookup("constructor")(E(), self.lookup("value").mul(that.lookup("value")));
            })

            //Division
            self.define("div", function (that) {
                return wrappers.int.lookup("constructor")(E(), self.lookup("value").div(that.lookup("value")));
            })

            //Modulo
            self.define("mod", function (that) {
                return wrappers.int.lookup("constructor")(E(), self.lookup("value").mod(that.lookup("value")));
            })

            //Less than
            self.define("lt", function (that) {
                return wrappers.bool.lookup("constructor")(E(), self.lookup("value").compareTo(that.lookup("value") < 0));
            })

            //Less than or equal to
            self.define("le", function (that) {
                return wrappers.bool.lookup("constructor")(E(), self.lookup("value").compareTo(that.lookup("value") <= 0));
            })

            //Greater than
            self.define("gt", function (that) {
                return wrappers.bool.lookup("constructor")(E(), self.lookup("value").compareTo(that.lookup("value") > 0));
            })

            //Greater than or equal to
            self.define("ge", function (that) {
                return wrappers.bool.lookup("constructor")(E(), self.lookup("value").compareTo(that.lookup("value") >= 0));
            })

            self.define("toString", function () {
                return wrappers.string.lookup("constructor")(E(), "" + self.lookup("value"));
            })

            return self;
        }

    })

    //Int64 wrapper
    this.long = new Environment({
        constructor(self, value) {
            self.parent = wrappers.int;
            if (value instanceof Environment && value.has("value")) {
                value = value.lookup("value");
            }

            //Define the basic value.
            self.define("value", new Int64(value));
            //Addition
            self.define("add", function (that) {

                return wrappers.long.lookup("constructor")(E(), self.lookup("value").add(that.lookup("value")));
            })
            //Subtraction
            self.define("sub", function (that) {

                return wrappers.long.lookup("constructor")(E(), self.lookup("value").sub(that.lookup("value")));
            })
            //Multiplication
            self.define("mul", function (that) {

                return wrappers.long.lookup("constructor")(E(), self.lookup("value").mul(that.lookup("value")));
            })
            //Division
            self.define("div", function (that) {

                return wrappers.long.lookup("constructor")(E(), self.lookup("value").div(that.lookup("value")));
            })

            //Modulo
            self.define("mod", function (that) {
                return wrappers.long.lookup("constructor")(E(), self.lookup("value").mod(that.lookup("value")));
            })


            //Less than
            self.define("lt", function (that) {

                return wrappers.bool.lookup("constructor")(E(), self.lookup("value").compareTo(that.lookup("value") < 0));
            })

            //Less than or equal to
            self.define("le", function (that) {

                return wrappers.bool.lookup("constructor")(E(), self.lookup("value").compareTo(that.lookup("value") <= 0));
            })

            //Greater than
            self.define("gt", function (that) {

                return wrappers.bool.lookup("constructor")(E(), self.lookup("value").compareTo(that.lookup("value") > 0));
            })

            //Greater than or equal to
            self.define("ge", function (that) {

                return wrappers.bool.lookup("constructor")(E(), self.lookup("value").compareTo(that.lookup("value") >= 0));
            })

            self.define("toString", function () {
                return wrappers.string.lookup("constructor")(E(), "" + self.lookup("value"));
            })

            return self;
        }
    });

    //Number wrapper
    this.double = new Environment({
        constructor(self, value) {
            self.parent = wrappers.int;
            if (value instanceof Environment && value.has("value")) {
                value = value.lookup("value");
            }

            //Define the basic value.
            self.define("value", value * 1);
            //Addition
            self.define("add", function (that) {

                return wrappers.double.lookup("constructor")(E(), self.lookup("value") + (that.lookup("value")));
            })
            //Subtraction
            self.define("sub", function (that) {

                return wrappers.double.lookup("constructor")(E(), self.lookup("value") - (that.lookup("value")));
            })
            //Multiplication
            self.define("mul", function (that) {

                return wrappers.double.lookup("constructor")(E(), self.lookup("value") * (that.lookup("value")));
            })
            //Division
            self.define("div", function (that) {

                return wrappers.double.lookup("constructor")(E(), self.lookup("value") / (that.lookup("value")));
            })

            //Modulo
            self.define("mod", function (that) {
                return wrappers.double.lookup("constructor")(E(), self.lookup("value") % (that.lookup("value")));
            })


            //Less than
            self.define("lt", function (that) {

                return wrappers.bool.lookup("constructor")(E(), self.lookup("value") < (that.lookup("value")));
            })

            //Less than or equal to
            self.define("le", function (that) {

                return wrappers.bool.lookup("constructor")(E(), self.lookup("value") <= (that.lookup("value")));
            })

            //Greater than
            self.define("gt", function (that) {

                return wrappers.bool.lookup("constructor")(E(), self.lookup("value").compareTo(that.lookup("value") > 0));
            })

            //Greater than or equal to
            self.define("ge", function (that) {

                return wrappers.bool.lookup("constructor")(E(), self.lookup("value").compareTo(that.lookup("value") >= 0));
            })

            self.define("toString", function () {
                return wrappers.string.lookup("constructor")(E(), "" + self.lookup("value"));
            })

            return self;
        }
    })


    this.bool = new Environment({
        constructor(self, value) {
            if (value instanceof Environment && value.has("value")) {
                value = value.lookup("value");
            }

            self.define("value", !falsey.includes(JSON.stringify(value)))
            self.define("toString", function () {
                return wrappers.string.lookup("constructor")(E(), "" + self.lookup("value"));
            })
            return self;
        }
    })

    this.string = new Environment({
        constructor(self, value) {
            if (value instanceof Environment && value.has("value")) {
                value = value.lookup("value");
            }

            self.define("value", "" + value);
            self.define("length", function () {
                return self.lookup("value").length;
            })

            self.define("charAt", function (i) {
                var t = i.lookup("value").toNumber();
                if (t >= 0) {
                    return wrappers.string.lookup("constructor")(E(), self.lookup("value").charAt(t));
                } else {
                    return wrappers.string.lookup("constructor")(E(), self.lookup("value").charAt(self.lookup("value").length + t));
                }
            })

            self.define("toString", function () {
                return self;
            })

            return self;
        }

    })

    this.void = new Environment({
        constructor(self) {
            self.define("value", null);
            self.define("toString", function () {
                return wrappers.string.lookup("constructor")(E(), "null");
            })

            return self;
        }
    })

}