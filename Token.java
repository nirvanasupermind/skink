package com.github.skink;

public class Token {
	private int beginIndex;
	private int endIndex;
	private TokenType tokenType;
	private String tokenString;

	public Token(int beginIndex, int endIndex, String tokenString, TokenType tokenType) {
		this.beginIndex = beginIndex;
		this.endIndex = endIndex;
		this.tokenType = tokenType;
		this.tokenString = tokenString;
	}

	public int getBegin() {
		return this.beginIndex;
	}

	public int getEnd() {
		return this.endIndex;
	}

	public String getTokenString() {
		return this.tokenString;
	}

	public TokenType getTokenType() {
		return this.tokenType;
	}

	public String toString() {
		return String.format("(%s, %s)", this.tokenType.toString(), this.tokenString);
	}
}