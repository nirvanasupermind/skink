package skink;

import java.lang.*;
import java.util.*;
import skink.Constants;
import skink.ParseError;
import skink.ParseResult;

public class Parser {
    public String text;
    public int pos;
    public Character currentChar;
    
    public Parser(String text) {
        this.text = text;
        this.pos = -1;
        this.advance();
    }

    public void advance() {
        this.pos++;
        if(this.pos < this.text.length()) {
            this.currentChar = this.text.charAt(this.pos);
        } else {
            this.currentChar = null;
        }
    }

    public ParseResult parse() {
        return this.parseInt();
    }

    public ParseResult parseInt() {
        return new ParseResult(new HashMap<String, Object>() {{
            put("x", 2);
        }}, null);
    }
}
