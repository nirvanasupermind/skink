package skink;

import java.lang.*;
import java.util.ArrayList;

public class Parser {
    public ArrayList<Token> tokens;
    public int index;
    
    public Parser(ArrayList<Token> tokens) {
        this.tokens = tokens;
        this.advance();
    }

    public void advance() {
        this.index++;
        return this.tokens.get(this.index);
    }
}