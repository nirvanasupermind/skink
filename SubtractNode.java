package com.github.skink;

public class SubtractNode extends Node {
    public Node nodeA;
    public Node nodeB;

    public SubtractNode(Node nodeA, Node nodeB, int line) {
        this.nodeA = nodeA;
        this.nodeB = nodeB;
        this.line = line;
    }

    public String toString() {
        return String.format("(subtract %s %s)", this.nodeA, this.nodeB);
    }
}