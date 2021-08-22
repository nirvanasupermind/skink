package skink;

import java.lang.*;

public class Token {
    public final TokenType type;
    public final String value;
    public final int pos;

    public Token(TokenType type, String value, int pos) {
        this.type = type;
        this.value = value;
        this.pos = pos;
    }
}