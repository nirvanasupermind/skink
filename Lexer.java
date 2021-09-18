package com.github.skink;

import java.util.LinkedList;

public class Lexer {
    private static String scan(char firstChar, PeekableStream chars, String allowed) {
        String ret = String.valueOf(firstChar);
        int p = chars.next;

        while(p != '\0' && allowed.indexOf(p) != -1) {
            ret += chars.moveNext();
            p = chars.next;
        }

        return ret;
    }

    public static LinkedList<Token> lex(String file, String source) {
        LinkedList<Token> tokens = new LinkedList<Token>();
        
        PeekableStream chars = new PeekableStream(source);
        int line = 1;

        while(chars.next != '\0') {
            char c = chars.moveNext();
            if(Constants.WHITESPACE.indexOf(c) != -1) {

            } else if(Constants.NEWLINES.indexOf(c) != -1) {
                line++;
            } else if(c == '(') {
                tokens.add(new Token(line, TokenType.OPEN_BRACE, String.valueOf(c)));
            } else if(c == ')') {
                tokens.add(new Token(line, TokenType.CLOSE_BRACE, String.valueOf(c)));
            } else if(Constants.OPERATIONS.indexOf(c) != -1) {
                tokens.add(new Token(line, TokenType.OPERATION, String.valueOf(c)));
            } else if(Constants.DIGITS.indexOf(c) != -1) {
                String lexeme = Lexer.scan(c, chars, Constants.DIGITS + ".");
                if(lexeme.indexOf('.') != -1)
                    tokens.add(new Token(line, TokenType.FLOAT, lexeme));
                else
                    tokens.add(new Token(line, TokenType.INT, lexeme));
            } else {
                throw new SkinkException(file, line, "lexical error");
            }
        }

        return tokens;
    }
}