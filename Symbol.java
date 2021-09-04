package com.github.skink;

public abstract class Symbol {
	private int code;
	private String name;

	public Symbol(int code, String name) {
		this.code = code;
		this.name = name;
	}

	public int getCode() {
		return code;
	}

	public String getName() {
		return name;
	}

	public abstract boolean isTerminal();

	public abstract boolean isNonTerminal();

	public String toString() {
		return this.name; 
	}

	public int hashCode() {
		return this.code;
	}
}