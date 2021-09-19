package com.github.skink;

import java.util.LinkedList;

public class TokenStream {
    private final LinkedList<Token> tokens;
    private int position;
    public Token next;

    public TokenStream(LinkedList<Token> tokens) {
        this.tokens = tokens;
        this.position = -1;        
        this.fill();
    }

    private void fill() {
        this.position++;
        if(this.position >= this.tokens.size()) {
            this.next = null;
        } else {
            this.next = this.tokens.get(this.position);
        }
    }

    public Token moveNext() {
        Token ret = this.next;
        this.fill();
        return ret;
    }
}