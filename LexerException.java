package skink;

import java.lang.*;

public class LexerException extends RuntimeException {
    public LexerException(int index) {
        super(String.format("lexical error at position %s", index));
    }
}