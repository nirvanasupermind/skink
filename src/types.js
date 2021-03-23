var lynx = require("lynx-js");
var Environment = require("./Environment.js");

var Int = lynx.Int._.int(32);
var Long = lynx.Int;
var IntWrapper = new Environment({
    constructor(self, value) {
        self.define("value", new Int(value));
        self.define("add", function (other) {
            return IntWrapper.lookup("constructor")(new Environment({}), self.lookup("value").add(other.lookup("value")));
        });

        self.define("sub", function (other) {
            return IntWrapper.lookup("constructor")(new Environment({}), self.lookup("value").sub(other.lookup("value")));
        });

        self.define("mul", function (other) {
            return IntWrapper.lookup("constructor")(new Environment({}), self.lookup("value").mul(other.lookup("value")));
        });

        return self;
    }
})
module.exports = { Int, Long, IntWrapper }