package com.github.skink;

import java.util.List;

public class Skink {
    public static void run(String source) {
        Lexer lexer = new Lexer();
        lexer.tokenize(source);
        List<Token> tokens = lexer.getTokens();

        System.out.println("TOKENS: ");

        for(var i = 0; i < tokens.size(); i++) {
        System.out.println(tokens.get(i));
        }
    }
}