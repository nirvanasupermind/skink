import java.lang.*;
import skink.Lexer;

public class Test {
    public static void main(String[] args) { 
        String source = "echo \"Hello World\"\necho \"H\"";

        System.out.println(Lexer.lex(source));
    }
}