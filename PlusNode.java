package com.github.skink;

public class PlusNode extends Node {
    public Node node;

    public PlusNode(Node node, int line) {
        this.node = node;
        this.line = line;
    }

    public String toString() {
        return String.format("(plus %s)", this.node);
    }
}