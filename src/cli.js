#!/usr/bin/env node
var skink = require("./skink.js");
function complete(command_func) {
    return function (str) {
        var commands = command_func();
        // str = str.substring(str.indexOf("skink> "));
      var i;
      var ret = [];
      for (i=0; i< commands.length; i++) {
        if (commands[i].indexOf(str) == 0)
          ret.push(commands[i]);
      }

      return ret;
    };
};


var prompt = require("prompt-sync")({
    "history": require('prompt-sync-history')(), //open history file
    "autocomplete": complete(() => skink.KEYWORDS.concat(skink.global_scope.keys)),
    "sigint": false
});


//Grab provided args.
var args = process.argv.slice(2);
if (args[0] === "-e") {
    var temp = skink.run("<eval>", args[1]);
    if (temp[1]) {
        console.log(temp[1].toString());
    }

} else if (args.length >= 1) {
    var temp = skink(args[0]);
    if (temp[1]) {
        console.log(temp[1].toString());
    }
} else {
    //Shell

    console.log('Type "exit" to exit.')
    while (true) {
        var text = prompt("skink> ");
        if (text.replace(/\s*/m, "") === "") continue;
        if (text === "exit") break;

        var [result, error] = skink.run("<anonymous>", text);
        // console.log(result,error)
        if (error)
            console.log("" + error);
        else
            console.log("" + result);
    }
}

