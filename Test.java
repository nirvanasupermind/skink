import java.lang.*;
import java.util.ArrayList;
import skink.Skink;
import skink.Token;

public class Test {
    public static void main(String[] args) {
        String source = "(1 + 2) * 3";
        
        ArrayList<Token> tokens = Skink.runString(source);
        for(var i = 0; i < tokens.size(); i++) {
            System.out.print(tokens.get(i).type);
            System.out.print(":");
            System.out.println(tokens.get(i).value);
        }
    }
}