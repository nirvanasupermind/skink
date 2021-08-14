import java.lang.*;
import skink.Parser;
public class Test {  
    public static void main(String[] args) {
        String text = "2";
        System.out.println(new Parser(text).parse());
    }
}