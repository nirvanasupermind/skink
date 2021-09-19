package com.github.skink;

public class CharStream {
    private final String source;
    private int position;
    public char next;

    public CharStream(String source) {
        this.source = source;
        this.position = -1;        
        this.fill();
    }

    private void fill() {
        this.position++;
        if(this.position >= this.source.length()) {
            this.next = '\0';
        } else {
            this.next = this.source.charAt(this.position);
        }
    }

    public char moveNext() {
        char ret = this.next;
        this.fill();
        return ret;
    }
}