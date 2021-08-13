package skink;

import java.lang.*;

public class ParseError {
    public int pos;
    public ParseError(int pos) {
        this.pos = pos;
    }

    public String toString() {
        return "(pos="+String.valueOf(pos)+")";
    }
}