package com.github.skink;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Lexer {
	public static final String KEYWORDS = "true|false";

	private Map<TokenType, String> regEx;
	private List<Token> result;

	public Lexer() {
		regEx = new TreeMap<TokenType, String>();
		launchRegEx();
		result = new ArrayList<Token>();
	}

	public void tokenize(String source) {
		int position = 0;
		Token token = null;
		do {
			token = separateToken(source, position);
			if (token != null) {
				position = token.getEnd();
				result.add(token);
			}
		} while (token != null && position != source.length());
		if (position != source.length()) {
			throw new RuntimeException("Lexical error at position # "+ position);
		}
	}

	public List<Token> getTokens() {
		return result;
	}

	public List<Token> getFilteredTokens() {
		List<Token> filteredResult = new ArrayList<Token>();
		for (Token t : this.result) {
			if (!t.getTokenType().isAuxiliary()) {
				filteredResult.add(t);
			}
		}
		return filteredResult;
	}

	private Token separateToken(String source, int fromIndex) {
		if (fromIndex < 0 || fromIndex >= source.length()) {
			throw new IllegalArgumentException("Illegal index in the input stream!");
		}
		for (TokenType tokenType : TokenType.values()) {
			Pattern p = Pattern.compile(".{" + fromIndex + "}" + regEx.get(tokenType),
					Pattern.DOTALL);
			Matcher m = p.matcher(source);
			if (m.matches()) {
				String lexema = m.group(1);
				return new Token(fromIndex, fromIndex + lexema.length(), lexema, tokenType);
			}
		}

		return null;
	}

	private void launchRegEx() {
    	regEx.put(TokenType.WHITESPACE, "( ).*");
		regEx.put(TokenType.TAB, "(\t).*");
		regEx.put(TokenType.PLUS, "(\\+{1}).*");
		regEx.put(TokenType.MINUS, "(\\-{1}).*");
		regEx.put(TokenType.MULTIPLY, "(\\*).*");
		regEx.put(TokenType.DIVIDE, "(\\/).*");
		regEx.put(TokenType.MOD, "(%).*");
		regEx.put(TokenType.AND, "(&&).*");
		regEx.put(TokenType.OR, "(\\|\\|).*");
		regEx.put(TokenType.XOR, "(\\^\\^).*");
		regEx.put(TokenType.NOT, "(!!).*");
		regEx.put(TokenType.LBRACE, "(\\().*");
		regEx.put(TokenType.RBRACE, "(\\)).*");
		regEx.put(TokenType.INT, "\\b(\\d{1,9}(?![\\d.]))\\b.*");
		regEx.put(TokenType.FLOAT, "\\b(\\d{1,9}\\.\\d{1,32})\\b.*");
		regEx.put(TokenType.IDENTIFIER, String.format("(\\b(?!(?:%s)\\b)[a-z]+).*", Lexer.KEYWORDS));
		regEx.put(TokenType.KEYWORD, String.format("\\b(%s)\\b.*", Lexer.KEYWORDS));
	}
}