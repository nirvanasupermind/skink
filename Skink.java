package com.github.skink;

import java.util.LinkedList;

public class Skink {
    private static void run(String file, String source) {
        LinkedList<Token> tokens = Lexer.lex(file, source);
        System.out.println("tokens:");
        System.out.println(tokens);
    }
    
    public static void runString(String source) {
        run("<anonymous>", source);
    }
}