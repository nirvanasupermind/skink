package com.github.skink;

import java.util.ArrayList;
import java.util.List;

public class Parser {
    public final String file;
    public final List<Token> tokens;
    public int position;
    
    public Parser(String file, List<Token> tokens) {
        this.file = file;
        this.tokens = tokens;
        this.position = 0;
    }

    public void raiseError(Token token) {
        Errors.raiseError(file, token.line, "syntax error");
    }

    public void advance() {
        this.position++;
    }

    public Token current() {
        return this.tokens.get(this.position);
    }
    
    public Node parse() {
        Node result = this.expr();   
        if(this.current().type != TokenType.EOF) {
            this.raiseError(this.current());
        }

        return result;
    }

    public Node expr() {
        Node result = this.term();

        while(this.current().type != TokenType.EOF && (this.current().type == TokenType.PLUS || this.current().type == TokenType.MINUS)) {
            if(this.current().type == TokenType.PLUS) {
                this.advance();
                result = new AddNode(result, this.term(), result.line);
            } else if(this.current().type == TokenType.MINUS) {
                this.advance();
                result = new SubtractNode(result, this.term(), result.line);
            }
        }

        return result;
    }

    public Node term() {
        Node result = this.factor();

        while(this.current().type != TokenType.EOF && (this.current().type == TokenType.MULTIPLY || this.current().type == TokenType.DIVIDE || this.current().type == TokenType.MOD)) {
            if(this.current().type == TokenType.MULTIPLY) {
                this.advance();
                result = new MultiplyNode(result, this.factor(), result.line);
            } else if(this.current().type == TokenType.DIVIDE) {
                this.advance();
                result = new DivideNode(result, this.factor(), result.line);
            } else if(this.current().type == TokenType.MOD) {
                this.advance();
                result = new ModNode(result, this.factor(), result.line);
            }
        }

        return result;
    }

    public Node factor() {
        Token token = this.current();
        if(token.type == TokenType.LPAREN) {
            this.advance();
            Node result = this.expr();
            if(this.current().type != TokenType.RPAREN)
                this.raiseError(this.current());
            
            this.advance();

            return result;
        } else if(token.type == TokenType.INT) {
            this.advance();
            return new IntNode(token, token.line);
        } else if(token.type == TokenType.FLOAT) {
            this.advance();
            return new FloatNode(token, token.line);
        } else if(token.type == TokenType.PLUS) {
            this.advance();
            Node factor = this.factor();
            return new PlusNode(factor, factor.line);
        } else if(token.type == TokenType.MINUS) {
            this.advance();
            Node factor = this.factor();
            return new MinusNode(factor, factor.line);
        } else {
            this.raiseError(this.current());
            return null;
        }
    }
}