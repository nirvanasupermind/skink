package skink;

import java.lang.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Lexer {
    public HashMap<TokenType, String> regEx;
    public ArrayList<Token> tokens;

    public Lexer() {
        this.regEx = new HashMap<TokenType, String>();
        this.launchRegEx();
        this.tokens = new ArrayList<Token>();
    }

    public void tokenize(String source)  {
		int position = 0;
		Token token = null;
		do {
			token = separateToken(source, position);
			if (token != null) {
				position = token.endIndex;
				this.tokens.add(token);
			}

		} while (token != null && position != source.length());
        if (position != source.length()) {
			throw new LexerException(position);
		}
	}

    public Token separateToken(String source, int fromIndex) {
		if (fromIndex < 0 || fromIndex >= source.length()) {
            throw new LexerException(fromIndex);
		}

		for (TokenType tokenType : TokenType.values()) {
			Pattern p = Pattern.compile(".{" + fromIndex + "}" + regEx.get(tokenType),
					Pattern.DOTALL);
			Matcher m = p.matcher(source);
			if (m.matches()) {
				String lexema = m.group(1);
				return new Token(
                    tokenType, lexema, 
                    fromIndex, fromIndex + lexema.length()
                );
			}
		}

		return null;
	}

    public void launchRegEx() {
        regEx.put(TokenType.PLUS, "(\\+{1}).*");
        regEx.put(TokenType.MINUS, "(\\-{1}).*");
		regEx.put(TokenType.MULTIPLY, "(\\*{1}).*");
		regEx.put(TokenType.DIVIDE, "(\\/{1}).*");
		regEx.put(TokenType.MOD, "(%{1}).*");
		regEx.put(TokenType.OPEN_BRACE, "(\\().*");
		regEx.put(TokenType.CLOSE_BRACE, "(\\)).*");
    }
}