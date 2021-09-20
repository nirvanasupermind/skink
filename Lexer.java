package com.github.skink;

import java.util.LinkedList;

public class Lexer {
    private final String file;
    private final CharStream chars;

    public Lexer(String file, CharStream chars) {
        this.file = file;
        this.chars = chars;
    }

    private String scan(char firstChar, String allowed) {
        String ret = String.valueOf(firstChar);
        int p = this.chars.next;

        while(p != '\0' && allowed.indexOf(p) != -1) {
            ret += this.chars.moveNext();
            p = this.chars.next;
        }

        return ret;
    }

    public LinkedList<Token> lex() {
        LinkedList<Token> tokens = new LinkedList<Token>();
        
        int line = 1;

        while(this.chars.next != '\0') {
            char c = this.chars.moveNext();
            if(Constants.WHITESPACE.indexOf(c) != -1) {
                
            } else if(Constants.NEWLINES.indexOf(c) != -1) {
                // tokens.add(new Token(line, TokenType.NEWLINE, String.valueOf(c)));
                line++;
            } else if(c == '(') {
                tokens.add(new Token(line, TokenType.OPEN_BRACE, String.valueOf(c)));
            } else if(c == ')') {
                tokens.add(new Token(line, TokenType.CLOSE_BRACE, String.valueOf(c)));
            } else if(c == '+') {
                tokens.add(new Token(line, TokenType.PLUS, String.valueOf(c)));
            } else if(c == '-') {
                tokens.add(new Token(line, TokenType.MINUS, String.valueOf(c)));
            } else if(c == '*') {
                tokens.add(new Token(line, TokenType.MULTIPLY, String.valueOf(c)));
            } else if(c == '/') {
                tokens.add(new Token(line, TokenType.DIVIDE, String.valueOf(c)));
            } else if(c == '%') {
                tokens.add(new Token(line, TokenType.MOD, String.valueOf(c)));
            } else if(Constants.DIGITS.indexOf(c) != -1) {
                String value = this.scan(c, Constants.DIGITS + ".");
                if(value.indexOf('.') != -1)
                    tokens.add(new Token(line, TokenType.FLOAT, value));
                else
                    tokens.add(new Token(line, TokenType.INT, value));
            } else {
                throw new SkinkException(this.file, line, "lexical error");
            }
        }

        tokens.add(new Token(line, TokenType.EOF, ""));


        return tokens;
    }
}