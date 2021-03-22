var Environment = require("./Environment.js")
var lynx = require("lynx-js");
var Environment = require("./Environment.js");

Function.prototype.clone = function() {
    var that = this;
    var temp = function temporary() { return that.apply(this, arguments); };
    for(var key in this) {
        if (this.hasOwnProperty(key)) {
            temp[key] = this[key];
        }
    }
    return temp;
};


var types = new (function () {
    //struct for user-defined lambdas
    function createLambda(params, body, env) {
        return { params, body, env }
    }

    function createWrapper(fun, other=[]) {
        return new Environment(new (function () {
            this.constructor = createLambda(
                ["this", "value"],
                ["begin",
                        ["set", ["prop", "this", '"value"'], [fun, "value"]],
                        ...other],
                Environment.GlobalEnvironment
            );
        }));
    }


    this.Int = createWrapper("__int");
    this.Long = createWrapper("__long");
    this.Double = createWrapper("__double");
    this.String = createLambda("__string");
    this.Boolean = createWrapper("__bool");
    this.typeEnv = new Environment({
        int: this.Int,
        long: this.Long,
        double: this.Double,
        string: this.String
    })
})();


module.exports = types;