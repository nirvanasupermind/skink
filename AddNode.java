package com.github.skink;

public class AddNode extends Node {
    public Node nodeA;
    public Node nodeB;

    public AddNode(Node nodeA, Node nodeB, int line) {
        this.nodeA = nodeA;
        this.nodeB = nodeB;
        this.line = line;
    }

    public String toString() {
        return String.format("(add %s %s)", this.nodeA, this.nodeB);
    }
}