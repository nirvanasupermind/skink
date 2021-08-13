package skink;

import java.lang.*;
import skink.Constants;
import skink.ParseError;

public class Parser {
    String text;
    int pos;

    public Parser(String text) {
        this.text = text;
        this.reset();
    }

    public void advance() {
        this.pos++;
    }

    public void reverse() {
        this.pos--;
    }

    public void reset() {
        this.pos = -1;
        this.advance();
        this.skipWhitespace();
    }

    public void skipWhitespace() {
        while(Constants.WHITESPACE.indexOf(this.currentChar()) >= 0) {
            this.advance();
        }
    }

    public char currentChar() {
        if(this.pos >= this.text.length()) {
            return '\0';
        } else {
            return this.text.charAt(this.pos);
        }
    }

    public ParseState parseInt() {
        ParseState s = new ParseState();
        String str = "";

        while(Constants.DIGITS.indexOf(this.currentChar()) >= 0) {
            str += this.currentChar();
            this.advance();
        }
        
        return s.setNode(new Node("int", str));
    }

    public ParseState parseFloat() {
        ParseState s = new ParseState();
        Node intPart = s.register(this.parseInt());
        if(s.hasError()) { return s; }

        if(this.currentChar() != '.') {
            return s.setError(new ParseError(this.pos));
        }

        this.advance();
        Node fracPart = s.register(this.parseInt());
        if(s.hasError()) { return s; }
        return s.setNode(new Node("float", String.format("%s.%s", intPart.value, fracPart.value)));
    }

    public ParseState parseAtom() {
        ParseState s = new ParseState();
        Node floatNode = s.register(this.parseFloat());
        if(s.hasError()) {
            s.setError(null);
            this.reset();

            Node intNode = s.register(this.parseInt());
            if(s.hasError()) { return s; }

            return s.setNode(intNode);
        } else {
            return s.setNode(floatNode);
        }
    }  

    // public ParseState parseTerm() {
    //     ParseState s = new ParseState();
    //     Node left = s.register(this.parseAtom());
    //     if(s.hasError()) { return s; }

    //     s.advance();
    //     this.skipWhitespace()        
    // }  

    public ParseState parse() {
        ParseState s = new ParseState();

        Node node = s.register(this.parseAtom());
        if(s.hasError()) { return s; }

        this.skipWhitespace();
        if(this.currentChar() != '\0') {
            return s.setError(new ParseError(this.pos));
        }
        
        return s.setNode(node);
    }  
      
}
