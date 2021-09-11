package com.github.skink;

public class Skink {
    private static void run(String file, String text) {
        Lexer lexer = new Lexer(file, text);
        System.out.println(String.format("tokens: %s", lexer.getTokens()));
    }

    public static void runText(String text) {
        run("<anonymous>", text);
    }
}