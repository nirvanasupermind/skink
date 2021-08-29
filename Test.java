import skink.Lexer;

public class Test {
    public static void main(String[] args) {
        String code = "2.5 * 2.5";
        Lexer lexer = new Lexer(code);
        
        System.out.println(lexer.getTokens());
    }
}