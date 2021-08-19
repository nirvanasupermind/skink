var moo = require("moo");
var LangError = require("./LangError.js");

class Parser {
    constructor(tokens) {
        this.tokens = tokens.filter((token) => token.type !== "WS");
        this.idx = -1;
        this.advance();
    }

    raiseError(token) {
        var msg = moo.compile({}).formatError(token, "invalid syntax").split("\n")[0].slice(0, -1);
        new LangError(msg, token.offset).raise();
    }

    advance() {
        this.idx += 1;
        if (this.idx >= this.tokens.length) {
            this.currentToken = this.tokens[this.tokens.length - 1];
        } else {
            this.currentToken = this.tokens[this.idx]
        }
    }

    parse() {
        var result = this.expr();
        this.advance();
        if (this.currentToken.type !== "eof") {
            this.raiseError(this.currentToken);
        }

        return result;
    }

    expr() {
        return this.addExpr();
    }

    addExpr() {
        var left = this.mulExpr();
        while (this.currentToken.type === "plus" || this.currentToken.type === "minus") {
            var token = this.currentToken;

            this.advance();
            var right = this.mulExpr();
            
            if (token.type === "plus") {
                left = {
                    type: "plus",
                    value: [left, right],
                    offset: left.offset
                };
            } else {
                left = {
                    type: "minus",
                    value: [left, right],
                    offset: left.offset
                };
            }
        }

        return left;
    }
    
    mulExpr() {
        var left = this.atom();
        while (this.currentToken.type === "mul" || this.currentToken.type === "div" || this.currentToken.type === "mod") {
            var token = this.currentToken;

            this.advance();
            var right = this.atom();
            
            if (token.type === "mul") {
                left = {
                    type: "mul",
                    value: [left, right],
                    offset: left.offset
                };
            } else if(token.type === "div") {
                left = {
                    type: "div",
                    value: [left, right],
                    offset: left.offset
                };
            } else {
                left = {
                    type: "mod",
                    value: [left, right],
                    offset: left.offset
                };
            }
        }

        return left;
    }
    
    atom() {
        var token = this.currentToken;

        if (token.type === "int") {
            this.advance();
            return {
                type: "int",
                value: token.value,
                offset: token.offset
            };
        } else if (token.type === "float") {
            this.advance();
            return {
                type: "float",
                value: token.value,
                offset: token.offset
            };
        } else if (token.type === "plus") {
            this.advance();
            var atom = this.atom();

            return {
                type: "uplus",
                value: [atom],
                offset: token.offset
            };
        } else if (token.type === "minus") {
            this.advance();
            var atom = this.atom();

            return {
                type: "uminus",
                value: atom,
                offset: token.offset
            };
        } else if (token.type === "lparen") {
            this.advance();
            var expr = this.expr();
            if (this.currentToken.type !== "rparen") {
                this.raiseError(this.currentToken);
            }

            this.advance();
            return expr;
        } else {
            this.raiseError(this.currentToken);
        }
    }
}

module.exports = Parser;