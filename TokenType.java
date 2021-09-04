package com.github.skink;

public enum TokenType {
	WHITESPACE,
	TAB,
    PLUS,
	MINUS,
	MULTIPLY,
	DIVIDE,
	MOD,
	AND,
	OR,
	XOR,
	NOT,
	LBRACE,
	RBRACE,
	INT,
	FLOAT,
	IDENTIFIER,
	KEYWORD;

	public boolean isAuxiliary() {
		return this == WHITESPACE 
			   || this == TAB;
	}
}