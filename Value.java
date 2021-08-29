package skink;

import java.util.HashMap;

public class Value {
    public HashMap<String, Value> slots = new HashMap<String, Value>();
    public Value parent;
    public int line;

    public Value() {
        this.parent = null;
    }

    public Value(Value parent) {
        this.parent = parent;
    }

    public Value setLine(int line) {
        this.line = line;
        return this;
    }
    
    public Value put(String key, Value value) {
        this.slots.put(key, value);
        return value;
    }

    public Value get(String key) {
        if(!this.slots.containsKey(key)) {
            if(this.parent != null) {
                return this.parent.get(key);
            } else {
                return null;
            }
        } else {
            return this.slots.get(key);
        }
    }
}