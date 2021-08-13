package skink;

import java.lang.*;
import java.util.Arrays;
import skink.ParseError;
import skink.ParseState;

public class Node {
    public String name;
    public String value;
    public Node[] children;

    public Node(String name, String value) {
        this.name = name;
        this.value = value;
        this.children = new Node[0];
    }

    public Node(String name, Node[] children) {
        this.name = name;
        this.value = null;
        this.children = children;
    }

    public String toString() {
        return String.format("Node(name=%s, value=%s, children=%s)", this.name, this.value, Arrays.deepToString(this.children));
    }
}