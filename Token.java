package com.github.skink;

public class Token {
    public TokenType type;
    public String value;
    public int line;
    public Token(TokenType type, String value, int line) {
        this.type = type;
        this.value = value;
        this.line = line;
    }

    public String toString() {
        return String.format("%s:%s", this.type, this.value);
    }
}