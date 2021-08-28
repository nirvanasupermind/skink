package skink;

public class Token {
    public TokenType type;
    public String value;
    public int index;

    public Token(TokenType type, String value, int index) {
        this.type = type;
        this.value = value;
    }

    public String toString() {
        return this.type.toString();
    }
}