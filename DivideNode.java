package com.github.skink;

public class DivideNode extends Node {
    public Node nodeA;
    public Node nodeB;

    public DivideNode(Node nodeA, Node nodeB, int line) {
        this.nodeA = nodeA;
        this.nodeB = nodeB;
        this.line = line;
    }

    public String toString() {
        return String.format("(divide %s %s)", this.nodeA, this.nodeB);
    }
}