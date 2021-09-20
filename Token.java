package com.github.skink;

public class Token {
    private final int line;
    private final TokenType type;
    private final String value;

    public Token(int line, TokenType type, String value) {
        this.line = line;
        this.type = type;
        this.value = value;
    }

    public int getLine() {
        return this.line;
    }

    public TokenType getType() {
        return this.type;
    }

    public String getValue() {
        return this.value;
    }

    @Override
    public String toString() {
        return String.format("(%s, %s)", this.type, this.value);
    }
}