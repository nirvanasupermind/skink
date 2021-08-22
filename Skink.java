package skink;

import java.lang.*;
import java.util.ArrayList;

public class Skink {
    public static ArrayList<Token> runString(String source) {
        Scanner scanner = new Scanner(source);

        return scanner.scanTokens(); 
    }
}