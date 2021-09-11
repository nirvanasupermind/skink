package com.github.skink;

import java.util.ArrayList;
import java.util.List;

public class Lexer {
    public final String file;
    public final String text;
    public int position;
    public int line;

    public Lexer(String file, String text) {
        this.file = file;
        this.text = text + '\0';
        this.position = 0;
        this.line = 1;
    }

    public char current() {
        return this.text.charAt(this.position);    
    }

    public void advance() {
        this.position++;
    }

    public List<Token> getTokens() {
        List<Token> tokens = new ArrayList<Token>();
        while(this.current() != '\0') {
            if(this.current() == '\n') {
                this.line++;
                this.advance();
            } else if(Constants.WHITESPACE.indexOf(this.current()) != -1) {
                this.advance();
            } else if(this.current() == '.' || Constants.DIGITS.indexOf(this.current()) != -1) {
                tokens.add(this.getNumber());
            } else if(this.current() == '+') {
                tokens.add(new Token(TokenType.PLUS, "+", line));
                this.advance();
            } else if(this.current() == '-') {
                tokens.add(new Token(TokenType.MINUS, "-", line));
                this.advance();
            } else if(this.current() == '*') {
                tokens.add(new Token(TokenType.MULTIPLY, "*", line));
                this.advance();
            } else if(this.current() == '/') {
                tokens.add(new Token(TokenType.DIVIDE, "/", line));
                this.advance();
            } else if(this.current() == '%') {
                tokens.add(new Token(TokenType.MOD, "%", line));
                this.advance();
            } else if(this.current() == '(') {
                tokens.add(new Token(TokenType.LPAREN, "(", line));
                this.advance();
            } else if(this.current() == ')') {
                tokens.add(new Token(TokenType.RPAREN, ")", line));
                this.advance();
            } else {
                Errors.raiseError(this.file, this.line, "lexical error");
            }
        }

        tokens.add(new Token(TokenType.EOF, "", line));
        this.advance();

        return tokens;
    }

    public Token getNumber() {
        int decimalPointCount = 0;
        String number = "" + this.current();
        this.advance();

        while(this.current() != '\0' && (this.current() == '.' || Constants.DIGITS.indexOf(this.current()) != -1)) {
            if(this.current() == '.') {
                decimalPointCount++;
                if(decimalPointCount > 1)
                    break;
            }

            number += this.current();
            this.advance();
        }

        if(decimalPointCount == 0 && number.charAt(0) != '.') {
            return new Token(TokenType.INT, number, this.line); 
        } else {
            return new Token(TokenType.FLOAT, number, this.line); 
        }
    }
}