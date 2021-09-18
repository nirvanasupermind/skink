package com.github.skink;

public class SkinkException extends RuntimeException {    
    private final String file;
    private final int line;
    private final String msg;

    public SkinkException(String file, int line, String msg) {
        super(String.format("%s:%s: error: %s", file, line, msg));
        
        this.file = file;
        this.line = line;
        this.msg = msg;
    }
}