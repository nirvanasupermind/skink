package com.github.skink;

public class MinusNode extends Node {
    public Node node;

    public MinusNode(Node node, int line) {
        this.node = node;
        this.line = line;
    }

    public String toString() {
        return String.format("(minus %s)", this.node);
    }
}