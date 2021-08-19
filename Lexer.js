var moo = require("moo");
var LangError = require("./LangError.js");

var lexer = moo.compile({
    WS: /[ \t]+/,
    comment: /\/\/.*?$/,
    int: /(?<![\d.])[0-9]+(?![\d.])/,
    float: /[0-9]+\.(?:[0-9]+\b)?|\.[0-9]+/,
    plus: "+",
    minus: "-",
    mul: "*",
    div: "/",
    mod: "%",
    lparen: "(",
    rparen: ")",
    newline: { match: /[\n\r;]/, lineBreaks: true },
})

function withEof(lexer, eof, text) {
    Object.assign(eof, {
        toString() { return this.value },
        text: text,
        offset: lexer.index,
        size: 0,
        lineBreaks: 0,
        line: lexer.line,
        col: lexer.col,
    });
}

class Lexer {
    constructor(text) {
        this.text = text;
    }

    lex() {
        lexer.reset(this.text);
        var tokens = []

        while (true) {
            try {
                var token = lexer.next();
                if (!token) { break; }

                tokens.push(token);
            } catch (e) {
                var lines = this.text.split("\n");
                var lineNumber, colNumber;
                e.message.replace(/invalid syntax at line (.*?) col (.*?):/g, (a, b, c) => {
                    lineNumber = parseInt(b);
                    colNumber = parseInt(c);
                });

                var offset = 0;
                for (var i = 0; i < lineNumber; i++) {
                    offset += lines[i].length;
                }

                offset += colNumber;
                new LangError(e.message.split("\n")[0].slice(0, -1), offset).raise();
            }
        }

        var eof = { type: "eof", value: "<eof>" }
        withEof(lexer, eof, this.text);

        tokens.push(eof);

        return tokens;
    }
}

module.exports = Lexer;