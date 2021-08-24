package skink;

import java.lang.*;

public class Token {
    TokenType tokenType;
    String tokenString;
    int startIndex;
    int endIndex;

    public Token(TokenType tokenType, String tokenString, int startIndex, int endIndex) {
        this.tokenType = tokenType;
        this.tokenString = tokenString;
        this.startIndex = startIndex;
        this.endIndex = endIndex;
	  }

    //for debugging
    public String toString() {
      return String.format("(%s, %s)", this.tokenType, this.tokenString);
    }
}