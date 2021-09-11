package com.github.skink;

public class IntNode extends Node {
    public Token token;

    public IntNode(Token token, int line) {
        this.token = token;
        this.line = line;
    }

    public String toString() {
        return String.format("(int %s)", this.token.value);
    }
}