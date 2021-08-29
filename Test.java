import skink.Lexer;

public class Test {
    public static void main(String[] args) {
        Lexer lexer = new Lexer("5 + 5");

        System.out.println(lexer.getTokens());
    }
}