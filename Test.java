import skink.Lexer;

public class Test {
    public static void main(String[] args) {
        Lexer lexer = new Lexer("text");
        lexer.advance();
        lexer.advance();
        
        System.out.println(lexer.currentChar);
    }
}