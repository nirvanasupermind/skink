package com.github.skink;

import java.util.LinkedList;

public class Skink {
    private static void run(String file, String source) {
        Lexer lexer = new Lexer(file, new CharStream(source));
        LinkedList<Token> tokens = lexer.lex();

        Parser parser = new Parser(file, new TokenStream(tokens));
        Node node = parser.parse();

        System.out.println("tree:");
        System.out.println(node);
    }
    
    public static void runString(String source) {
        run("<anonymous>", source);
    }
}