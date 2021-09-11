package com.github.skink;

public class ModNode extends Node {
    public Node nodeA;
    public Node nodeB;

    public ModNode(Node nodeA, Node nodeB, int line) {
        this.nodeA = nodeA;
        this.nodeB = nodeB;
        this.line = line;
    }

    public String toString() {
        return String.format("(mod %s %s)", this.nodeA, this.nodeB);
    }
}