//Skink source code
//Usage permitted under terms of MIT License

"use strict";
//this file for exception class

//get line index
function get_ln(text, pos) {
    var tempString = text.substring(0, pos);
    return tempString.split("\n").length;
}

//get column index
function get_col(text, pos) {
    var tempString = text.substring(0, pos);
    return tempString.split("\n")[get_ln(text, pos) - 1].length + 1;
}

//An exception class.
function Exception(message, locations, input, file = "<anonymous>") {
    this.message = "" + message;
    this.locations = locations.map(parseFloat);
    this.input = "" + input;
    this.file = "" + file;
}



Exception.prototype.set_locations = function (locations) {
    return Object.setPrototypeOf(
        Object.assign(Object.assign({}, this), { "locations": locations }),
        Exception.prototype
    );
}


Exception.prototype.set_input = function (input) {
    return Object.setPrototypeOf(
        Object.assign(Object.assign({}, this), { "input": input }),
        Exception.prototype
    );
}


Exception.prototype.set_file = function (file) {
    return Object.setPrototypeOf(
        Object.assign(Object.assign({}, this), { "file": file }),
        Exception.prototype
    );
}


//Returns a description of the exception.
Exception.prototype.toString = function () {

    var result = "Exception: " + this.message;
    for (var i = 0; i < this.locations.length; i++) {
        result += this.at_msg(this.locations[i]);
    }

    return result;
}

Exception.prototype.at_msg = function (pos) {
    var [ln, col] = [get_ln(this.input, pos), get_col(this.input, pos)];
    return "\n\t" + " at " + this.file + ":" + ln + ":" + col;
}

module.exports = Exception;
