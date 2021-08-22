package skink;

import java.lang.*;
import java.util.ArrayList;

public class Scanner {
    public final String source;
    public ArrayList<Token> tokens = new ArrayList<Token>();
    public int pos;

    public Scanner(String source) {
        this.source = source;
        this.pos = -1;
        advance();
    }

    public void advance() {
        this.pos++;
    }
    
    public char getCurrentChar() {
        return this.source.charAt(this.pos);
    }

    public boolean isAtEnd() {
        return this.pos >= this.source.length();
    }

    public ArrayList<Token> scanTokens() {
        while(!this.isAtEnd()) { 
            char c = this.getCurrentChar();

            switch (c) {
                case ' ':
                case '\t':
                    this.advance(); 
                    break;
                case '0':
                case '1':
                case '2':
                case '3':
                case '4':
                case '5':
                case '6':
                case '7':
                case '8':
                case '9':
                    this.tokens.add(this.generateNumber());
                    this.advance();
                    break;
                case '+': 
                    this.tokens.add(new Token(TokenType.PLUS, null, this.pos));
                    this.advance();
                    break;
                case '-': 
                    this.tokens.add(new Token(TokenType.MINUS, null, this.pos));
                    this.advance();
                    break;
                case '*': 
                    this.tokens.add(new Token(TokenType.MUL, null, this.pos));
                    this.advance();
                    break;     
                case '/': 
                    this.tokens.add(new Token(TokenType.DIV, null, this.pos));
                    this.advance();
                    break;
                case '%': 
                    this.tokens.add(new Token(TokenType.MOD, null, this.pos));
                    this.advance();
                    break;
                case '(':
                    this.tokens.add(new Token(TokenType.LPAREN, null, this.pos));
                    this.advance();
                    break;
                default:
                    this.tokens.add(new Token(TokenType.RPAREN, null, this.pos));
                    this.advance();
                    break;
            }
        }

        this.tokens.add(new Token(TokenType.EOF, null, this.pos));
        return tokens;
    }

    public Token generateNumber() {
        String number_str = "";
        int decimalPointCount = 0;
        int pos = this.pos;
    
        while(!this.isAtEnd() 
              && (Constants.DIGITS + ".").indexOf(this.getCurrentChar()) != -1) {
            if(this.getCurrentChar() == '.') {
                if(decimalPointCount == 1) 
                    break;

                number_str += '.';
                decimalPointCount++;
            } else {
                number_str += this.getCurrentChar();
            }

            this.advance();
        }

        if(decimalPointCount == 0) {
            return new Token(TokenType.INT, number_str, pos);
        } else {
            return new Token(TokenType.FLOAT, number_str, pos);
        }
    }
}