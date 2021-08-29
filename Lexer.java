package skink;

import java.util.ArrayList;

public class Lexer {
    public String text;
    public char current;
    public int index;
    public int line;

    public Lexer(String text) {
        this.text = text;
        this.index = -1;
        this.line = 1;
        this.advance();
    }

    public boolean isAtEnd() {
       return this.index >= this.text.length();
    }

    public void advance() {
        this.index++;
        if(this.isAtEnd()) {
            this.current = '\0'; 
        } else {
            this.current = this.text.charAt(this.index);
        }

        if(this.current == '\n') {
            this.line++;
        }
   }
   
   public ArrayList<Token> getTokens() {
       ArrayList<Token> tokens = new ArrayList<Token>();
       while(!this.isAtEnd()) {
           if(Constants.WHITESPACE.indexOf(this.current) != -1) {
               this.advance();
           } else if(Constants.DIGITS.indexOf(this.current) != -1) {
               tokens.add(this.getNumber());   
           } else if(this.current == '+') {
               tokens.add(new Token(TokenType.PLUS, "+", this.line));
               this.advance();
           } else if(this.current == '-') {
               tokens.add(new Token(TokenType.MINUS, "-", this.line));
               this.advance();
           } else if(this.current == '*') {
               tokens.add(new Token(TokenType.MULTIPLY, "*", this.line));
               this.advance();
           } else if(this.current == '/') {
               tokens.add(new Token(TokenType.DIVIDE, "/", this.line));
               this.advance();
           } else if(this.current == '(') {
               tokens.add(new Token(TokenType.LPAREN, "(", this.line));
               this.advance();
           } else if(this.current == ')') {
               tokens.add(new Token(TokenType.RPAREN, ")", this.line));
               this.advance();
           } else if(this.current == ')') {
               tokens.add(new Token(TokenType.RPAREN, ")", this.line));
               this.advance();
           } else {
               Errors.report(
                   String.format("unexpected \"%s\"", this.current), 
                   this.line
               );
           }
       }

       tokens.add(new Token(TokenType.EOF, "", this.line));

       return tokens;
   }

   public Token getNumber() {
       int decimalPointCount = 0;
       int eCount = 0;

       String numberStr = Character.toString(this.current);
       this.advance();
       while(!this.isAtEnd() && (Constants.DIGITS + ".").indexOf(this.current) != -1) {
           if(this.current == '.') {
                decimalPointCount++;
                if(decimalPointCount > 1)
                    break;
           }

           numberStr += this.current;
           this.advance();
       }

       if(decimalPointCount == 0 && eCount == 0)
            return new Token(TokenType.INT, numberStr, this.line);
       else
            return new Token(TokenType.FLOAT, numberStr, this.line);  
   }
}