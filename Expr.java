package skink;

import java.lang.*;

public abstract class Expr { 
  public int pos;

  public static class Binary extends Expr {
    public final Expr left;
    public final Token operator;
    public final Expr right;
    public int pos;

    public Binary(Expr left, Token operator, Expr right) {
        this.left = left;
        this.operator = operator;
        this.right = right;
        this.pos = left.pos;
    }
  }

  public static class Unary extends Expr {
    public final Token operator;
    public final Expr left;
    public int pos;

    public Unary(Token operator, Expr left) {
    this.operator = operator;
      this.left = left;
      this.pos = left.pos;
    }
  }
}