package com.github.skink;

public class Errors {
    public static void raiseError(String file, int line, String message) {
        System.err.println(String.format("%s:%s: error: %s", file, line, message));
        System.exit(1);
    }
}