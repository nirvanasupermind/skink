import skink.Lexer;
import skink.Parser;

public class Test {
    public static void main(String[] args) {
        String code = "(1 + 2) * 3";

        Lexer lexer = new Lexer(code);
        Parser parser = new Parser(lexer.getTokens());
        
        System.out.println(parser.parse());
    }
}