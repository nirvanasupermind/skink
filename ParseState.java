package skink;

import java.lang.*;
import skink.Node;
import skink.ParseError;

public class ParseState {
    public Node node;
    public ParseError error;

    public ParseState() {
        this.node = null;
        this.error = null;
    }

    public ParseState setNode(Node node) {
        this.node = node;
        return this;
    }

    public ParseState setError(ParseError error) {
        this.error = error;
        return this;
    }

    public Node register(ParseState s) {
        this.error = s.error;
        return s.node;
    }

    public boolean hasError() {
        return this.error != null;
    }

    public String toString() {
        return String.format("ParseState(node=%s, error=%s)", this.node, this.error);
    }
}