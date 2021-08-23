package skink;

import java.lang.*;
import java.util.ArrayList;

public class Lexer {
    public static ArrayList<String> lex(String source) {
        ArrayList<String> tokens = new ArrayList<String>();
        String tok = "";
        String string = "";
        int isInString = 0;

        for(var i = 0; i < source.length(); i++) {
            char character = source.charAt(i);
            tok += character;

            if(tok.equals(" ")) {
                if(isInString == 0) {
                    tok = "";
                } else {
                    tok = " ";
                }
            } else if(tok.equals("\n")) {
                tok = "";
            } else if(tok.equals("echo")) {
                tokens.add("ECHO");
                tok = "";
            } else if(tok.equals("\"")) {
                if(isInString == 0) {
                    isInString = 1;
                } else if(isInString == 1) {
                    tokens.add("STRING:"+string.substring(1));
                    string = "";
                    isInString = 0;
                    tok = "";
                }
            } else if(isInString == 1) {
                string += tok;
                tok = "";
            }
        }

        return tokens;
    }
}