package com.github.skink;

import java.util.LinkedList;

public abstract class Node {
    public int line;

    public int getLine() {
        return this.line;
    }

    @Override
    public abstract String toString();

    public static class IntNode extends Node {
        private final Token token;

        public IntNode(int line, Token token) {
            this.line = line;
            this.token = token;
        }

        public Token getToken() {
            return this.token;
        }

        @Override
        public String toString() {
            return this.token.getValue();
        }
    }

    public static class FloatNode extends Node {
        private final Token token;

        public FloatNode(int line, Token token) {
            this.line = line;
            this.token = token;
        }

        @Override
        public String toString() {
            return this.token.getValue();
        }
    }

    public static class BinaryNode extends Node {
        private final Node nodeA;
        private final Token operation;
        private final Node nodeB;

        public BinaryNode(int line, Node nodeA, Token operation, Node nodeB) {
            this.line = line;
            this.nodeA = nodeA;
            this.operation = operation;
            this.nodeB = nodeB;
        }

        public Node getNodeA() {
            return this.nodeA;
        }

        public Token getOperation() {
            return this.operation;
        }

        public Node getNodeB() {
            return this.nodeB;
        }

        @Override
        public String toString() {
            return String.format("(%s %s %s)", this.operation.getValue(), this.nodeA, this.nodeB);
        }
    }    

    public static class UnaryNode extends Node {
        private final Token operation;
        private final Node nodeA;

        public UnaryNode(int line, Token operation, Node nodeA) {
            this.line = line;
            this.operation = operation;
            this.nodeA = nodeA;
        }

        public Token getOperation() {
            return this.operation;
        }

        public Node getNodeA() {
            return this.nodeA;
        }

        @Override
        public String toString() {
            return String.format("(%s %s)", this.operation.getValue(), this.nodeA);
        }
    }    
}