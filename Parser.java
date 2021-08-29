package skink;

import java.util.ArrayList;

public class Parser {
    public ArrayList<Token> tokens;
    public int index;

    public Parser(ArrayList<Token> tokens) {
        this.tokens = tokens;
        this.index = index;
    }

    public void error(Token token) {
        Errors.report(
            "syntax error",
            token.line
        );
    }

    public void advance() {
        this.index++;
    }

    public Token current() {
        if(this.index >= this.tokens.size()) {
            return this.tokens.get(this.tokens.size() - 1);
        } else {
            return this.tokens.get(this.index);
        }
    }

    public Node parse() {
        if(this.current().type == TokenType.EOF) {
            return new Node.EmptyNode(this.current().line);
        }

        Node node = this.expr();

        if(this.current().type != TokenType.EOF) {
            this.error(this.current());
        }

        return node;
    }

    public Node expr() {
        Node result = this.term();
        while(this.current().type != TokenType.EOF && (this.current().type == TokenType.PLUS || this.current().type == TokenType.MINUS)) {
            if(this.current().type == TokenType.PLUS) {
                this.advance();
                result = new Node.AddNode(result, this.term(), result.line);
            } else if(this.current().type == TokenType.MINUS) {
                this.advance();
                result = new Node.SubtractNode(result, this.term(), result.line);
            }
        }

        return result;
    }

    public Node term() {
        Node result = this.factor();
        while (this.current().type != TokenType.EOF && (this.current().type == TokenType.MULTIPLY || this.current().type == TokenType.DIVIDE || this.current().type == TokenType.MOD)) {
            if(this.current().type == TokenType.MULTIPLY) {
                this.advance();
                result = new Node.MultiplyNode(result, this.factor(), result.line);
            } else if(this.current().type == TokenType.DIVIDE) {
                this.advance();
                result = new Node.DivideNode(result, this.factor(), result.line);
            } else if(this.current().type == TokenType.MOD) {
                this.advance();
                result = new Node.ModNode(result, this.factor(), result.line);
            }
        }

        return result;
    }

    public Node factor() {
        Token token = this.current();
        if(token.type == TokenType.LPAREN) {
            this.advance();
            Node result = this.expr();

            if(this.current().type != TokenType.RPAREN) {
                this.error(this.current());
            }

            this.advance();
            return result;
        } else if(token.type == TokenType.INT) {
            this.advance();
            return new Node.IntNode(token, token.line);
        } else if(token.type == TokenType.FLOAT) {
            this.advance();
            return new Node.FloatNode(token, token.line);
        } else if(token.type == TokenType.PLUS) {
            this.advance();
            return new Node.PlusNode(this.factor(), token.line);
        } else if(token.type == TokenType.MINUS) {
            this.advance();
            return new Node.MinusNode(this.factor(), token.line);
        } else {
            this.error(token);
            return null; //dummy
        }
    }
}