package skink;

import java.lang.*;
import java.util.*;
import skink.ParseError;

public class ParseResult {
    public HashMap<String, Object> value;
    public ParseError error;
    public ParseResult() {
        this.value = null;
        this.error = null;
    }

    public ParseResult(HashMap<String, Object> value, ParseError error) {
        this.value = value;
        this.error = error;
    }
}