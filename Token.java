package com.github.skink;

public class Token {
    private final int line;
    private final TokenType type;
    private final String lexeme;

    public Token(int line, TokenType type, String lexeme) {
        this.line = line;
        this.type = type;
        this.lexeme = lexeme;
    }

    public int getLine() {
        return this.line;
    }

    public TokenType getType() {
        return this.type;
    }

    public String getLexeme() {
        return this.lexeme;
    }

    @Override
    public String toString() {
        return String.format("(%s, %s)", this.type, this.lexeme);
    }
}