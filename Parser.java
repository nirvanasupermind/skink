package com.github.skink;

import java.util.LinkedList;

public class Parser {
    LinkedList<Token> tokens;

    public Parser(LinkedList<Token> tokens);

    public static Node parse(LinkedList<Token> tokens);
}