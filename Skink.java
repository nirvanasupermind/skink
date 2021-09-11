package com.github.skink;

import java.util.List;

public class Skink {
    private static void run(String file, String text) {
        Lexer lexer = new Lexer(file, text);
        List<Token> tokens = lexer.getTokens();
    
        Parser parser = new Parser(file, tokens);
        Node tree = parser.parse();

        System.out.println(String.format("tree: %s", tree));
    }

    public static void runText(String text) {
        run("<anonymous>", text);
    }
}