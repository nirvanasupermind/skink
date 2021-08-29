package skink;

public class Errors {
    public static void report(String message, int line) {
        System.out.println(String.format("%s: error: %s", line, message));
        System.exit(0);
    }
}