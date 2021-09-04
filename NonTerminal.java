package com.github.skink;

public class NonTerminal extends Symbol {
	public NonTerminal(int code, String name) {
		super(code, name);
	}

	@Override
	public boolean equals(Object obj) {
		if (obj == this)
			return true;
		if (obj == null)
			return false;
		if (obj.getClass() != NonTerminal.class)
			return false;
		NonTerminal nts = (NonTerminal) obj;
		return this.getCode() == nts.getCode();
	}

	@Override
	public boolean isTerminal() {
		return false;
	}

	@Override
	public boolean isNonTerminal() {
		return true;
	}
}
