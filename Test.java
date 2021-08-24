import java.lang.*;
import skink.Lexer;

public class Test {
    public static void main(String[] args) {
        Lexer lexer = new Lexer();
        lexer.tokenize("+-*/%()");
        System.out.println(lexer.tokens);
    }
}