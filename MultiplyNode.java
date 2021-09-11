package com.github.skink;

public class MultiplyNode extends Node {
    public Node nodeA;
    public Node nodeB;

    public MultiplyNode(Node nodeA, Node nodeB, int line) {
        this.nodeA = nodeA;
        this.nodeB = nodeB;
        this.line = line;
    }

    public String toString() {
        return String.format("(multiply %s %s)", this.nodeA, this.nodeB);
    }
}