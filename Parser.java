package com.github.skink;

public class Parser {
    private final String file;
    private final TokenStream tokens;
    private Token current;

    public Parser(String file, TokenStream tokens) {
        this.file = file;
        this.tokens = tokens;   
        this.current = this.tokens.moveNext();
    }
    
    public void error(Token token) {
        throw new SkinkException(this.file, token.getLine(), "syntax error");
    }

    public void eat(TokenType type) {
        if(this.current.getType() == type) {
            this.current = this.tokens.moveNext();
        } else {
            this.error(this.current);  
        }
    }

    public Node parse() {
        Node node = this.addExpr();

        if(this.current.getType() != TokenType.EOF)
            this.error(this.current);
        
        return node;
    }

    public Node expr() {
        return this.addExpr();        
    }

    public Node addExpr() {
        Node node = this.subtractExpr();
        
        while(this.current.getType() == TokenType.PLUS) {
            Token token = this.current;
            this.eat(TokenType.PLUS);

            node = new Node.BinaryNode(node.getLine(), node, token, this.subtractExpr());
        }

        return node;
    }


    public Node subtractExpr() {
        Node node = this.multiplyExpr();
        
        while(this.current.getType() == TokenType.MINUS) {
            Token token = this.current;
            this.eat(TokenType.MINUS);

            node = new Node.BinaryNode(node.getLine(), node, token, this.multiplyExpr());
        }

        return node;
    }

 
    public Node multiplyExpr() {
        Node node = this.divideExpr();
        
        while(this.current.getType() == TokenType.MULTIPLY) {
            Token token = this.current;
            this.eat(TokenType.MULTIPLY);

            node = new Node.BinaryNode(node.getLine(), node, token, this.divideExpr());
        }

        return node;
    }   

    public Node divideExpr() {
        Node node = this.modExpr();
        
        while(this.current.getType() == TokenType.DIVIDE) {
            Token token = this.current;
            this.eat(TokenType.DIVIDE);

            node = new Node.BinaryNode(node.getLine(), node, token, this.modExpr());
        }

        return node;
    }   
    
    public Node modExpr() {
        Node node = this.unaryExpr();
        
        while(this.current.getType() == TokenType.MOD) {
            Token token = this.current;
            this.eat(TokenType.MOD);

            node = new Node.BinaryNode(node.getLine(), node, token, this.unaryExpr());
        }

        return node;
    }   

    public Node unaryExpr() {
        Token token = this.current;

        if(token.getType() == TokenType.PLUS) {
            this.eat(TokenType.PLUS);
            return new Node.UnaryNode(token.getLine(), token, this.braceExpr());
        } else if(token.getType() == TokenType.MINUS) {
            this.eat(TokenType.MINUS);
            return new Node.UnaryNode(token.getLine(), token, this.braceExpr());
        } else {
            return this.braceExpr();
        }
    }   

    public Node braceExpr() {
        Token token = this.current;

        if(token.getType() == TokenType.OPEN_BRACE) {
            this.eat(TokenType.OPEN_BRACE);
            Node expr = this.expr();
            this.eat(TokenType.CLOSE_BRACE);

            return expr;
        } else {
            return this.atom();
        }
    }   

    public Node atom() {
        Token token = this.current;
        
        if(token.getType() == TokenType.INT) {
            this.eat(TokenType.INT);
            return new Node.IntNode(token.getLine(), token);
        } else if(token.getType() == TokenType.FLOAT) {
            this.eat(TokenType.FLOAT);
            return new Node.FloatNode(token.getLine(), token);
        } else {
            this.error(token);
        }

        return null;
    }
}