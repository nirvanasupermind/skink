#!/usr/bin/env node
var skink = require("./skink.js");
var prompt = require("prompt-sync")();
//Grab provided args.
var args = process.argv.slice(2);
if(args.length === 0) {    
    //Shell

    console.log('Type "exit" to exit.')
    while(true) {    
        var text = prompt("skink> ");
        // if(text.replace(/\s*/m, "") === "") continue;
        if(text === "exit") break;

        var [result, error] = skink.run("<anonymous>", text);
        // console.log(result,error)
        if(error) 
            console.log("" + error);
        else
            console.log("" + result);
    }
}

