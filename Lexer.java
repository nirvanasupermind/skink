package skink;

public class Lexer {
    public String text;
    public int index;
    public char currentChar;

    public Lexer(String text) {
        this.text = text;
        this.index = -1;
        this.advance();
    }

    public void advance() {
        this.index++;
        if(this.index >= this.text.length()) {
            this.currentChar = '\0'; 
        } else {
            this.currentChar = this.text.charAt(this.index);
        }
    }
}