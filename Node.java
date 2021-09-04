package com.github.skink;

public class Node {
    public int beginIndex;
    public int endIndex;

    public static class IntNode extends Node {
        public final Token token;

        public IntNode(int beginIndex, int endIndex, Token token) {
            this.beginIndex = beginIndex;
            this.endIndex = endIndex;
            this.token = token;
        }
    }

    public static class FloatNode extends Node {
        public final Token token;

        public FloatNode(int beginIndex, int endIndex, Token token) {
            this.beginIndex = beginIndex;
            this.endIndex = endIndex;
            this.token = token;
        }
    }

    public static class UnaryNode extends Node {
        public final Node nodeA;

        public UnaryNode(int beginIndex, int endIndex, Node nodeA) {
            this.beginIndex = beginIndex;
            this.endIndex = endIndex;
            this.nodeA = nodeA;
        }
    }

    public static class BinaryNode extends Node {
        public final Node nodeA;
        public final Node nodeB;

        public BinaryNode(int beginIndex, int endIndex, Node nodeA, Node nodeB) {
            this.beginIndex = beginIndex;
            this.endIndex = endIndex;
            this.nodeA = nodeA;
            this.nodeB = nodeB;
        }
    }

    public static class PlusNode extends UnaryNode {
        public PlusNode(int beginIndex, int endIndex, Node nodeA) {
            super(beginIndex, endIndex, nodeA);
        }
    }

    public static class MinusNode extends UnaryNode {
        public MinusNode(int beginIndex, int endIndex, Node nodeA) {
            super(beginIndex, endIndex, nodeA);
        }
    }

    public static class AddNode extends BinaryNode {
        public AddNode(int beginIndex, int endIndex, Node nodeA, Node nodeB) {
            super(beginIndex, endIndex, nodeA, nodeB);
        }
    }

    public static class SubtractNode extends BinaryNode {
        public SubtractNode(int beginIndex, int endIndex, Node nodeA, Node nodeB) {
            super(beginIndex, endIndex, nodeA, nodeB);
        }
    }
 
    public static class MultiplyNode extends BinaryNode {
        public MultiplyNode(int beginIndex, int endIndex, Node nodeA, Node nodeB) {
            super(beginIndex, endIndex, nodeA, nodeB);
        }
    }

    public static class DivideNode extends BinaryNode {
        public DivideNode(int beginIndex, int endIndex, Node nodeA, Node nodeB) {
            super(beginIndex, endIndex, nodeA, nodeB);
        }
    }

    public static class ModNode extends BinaryNode {
        public ModNode(int beginIndex, int endIndex, Node nodeA, Node nodeB) {
            super(beginIndex, endIndex, nodeA, nodeB);
        }
    }

    public static class AndNode extends BinaryNode {
        public AndNode(int beginIndex, int endIndex, Node nodeA, Node nodeB) {
            super(beginIndex, endIndex, nodeA, nodeB);
        }
    }

    public static class OrNode extends BinaryNode {
        public OrNode(int beginIndex, int endIndex, Node nodeA, Node nodeB) {
            super(beginIndex, endIndex, nodeA, nodeB);
        }
    }  

    public static class XorNode extends BinaryNode {
        public XorNode(int beginIndex, int endIndex, Node nodeA, Node nodeB) {
            super(beginIndex, endIndex, nodeA, nodeB);
        }
    }    
}