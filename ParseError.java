package skink;

import java.lang.*;

public class ParseError {
    public int pos;
    public ParseError(int pos) {
        this.pos = pos;
    }

    public String toString() {
        return String.format("ParseError(pos=%s)", this.pos);
    }
}