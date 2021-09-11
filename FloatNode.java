package com.github.skink;

public class FloatNode extends Node {
    public Token token;

    public FloatNode(Token token, int line) {
        this.token = token;
        this.line = line;
    }

    public String toString() {
        return String.format("(float %s)", this.token.value);
    }
}