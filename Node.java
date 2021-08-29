package skink;

public class Node {
    public int line;
    public static class IntNode extends Node {
        public Token token;
        public IntNode(Token token, int line) {
            this.token = token;
            this.line = line;
        }

        public String toString() {
            return String.format("(int %s)", this.token.value);
        }
    }

    public static class FloatNode extends Node {
        public Token token;
        public FloatNode(Token token, int line) {
            this.token = token;
            this.line = line;
        }

        public String toString() {
            return String.format("(float %s)", this.token.value);
        }
    }

    public static class EmptyNode extends Node {
        public EmptyNode(int line) {
            this.line = line;
        }

        public String toString() {
            return "";
        }
    }

    public static class AddNode extends Node {
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

    public static class SubtractNode extends Node {
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

    public static class MultiplyNode extends Node {
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

    public static class DivideNode extends Node {
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

    public static class ModNode extends Node {
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

    public static class PlusNode extends Node {
        public Node nodeA;

        public PlusNode(Node nodeA, int line) {
            this.nodeA = nodeA;
            this.line = line;
        }

        public String toString() {
            return String.format("(plus %s)", this.nodeA);
        }
    }

    public static class MinusNode extends Node {
        public Node nodeA;

        public MinusNode(Node nodeA, int line) {
            this.nodeA = nodeA;
            this.line = line;
        }

        public String toString() {
            return String.format("(minus %s)", this.nodeA);
        }
    }
}