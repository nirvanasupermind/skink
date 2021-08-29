package skink;

public class Token {
    public TokenType type;
    public String value;
    public int line;

    public Token(TokenType type, String value, int index) {
        this.type = type;
        this.value = value;
    }

    //for debugging
    public String toString() {
        return String.format("(%s, %s)", this.type.toString(), this.value.toString());
    }
}