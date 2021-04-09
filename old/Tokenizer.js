/**
 * Tokenizer class.
 * Lazily pulls a token from a stream.
 */
class Tokenizer {
    /**
     * Initializes the string.
     */
    init(string) {
        this._string = string;
        this._cursor = 0;
    }

    advance() {
        this._cursor++;
    }

    /**
     * Whether we still have more tokens.
     */
    hasMoreTokens() {
        return this._cursor < this._string.length;
    }

    /**
     * Whether the tokenizer reached EOF.
     */
    isEOF() {
        return this._cursor === this._string.length;
    }

    /**
     * Obtains next token.
     */
    getNextToken() {
        if (!this.hasMoreTokens()) {
            return null;
        }

        const string = this._string.slice(this._cursor);

        //Numbers:
        if (!Number.isNaN(parseFloat(string.charAt(0)))) {
            let number = '';
            while (!Number.isNaN(parseFloat(string.charAt(this._cursor))) && this.hasMoreTokens()) {
                number += string.charAt(this._cursor++);
            }

            return {
                "type": "NUMBER",
                "value": number
            }
        }

        //Strings:
        if(string.charAt(0) === '"') {
            let s = "";
            do {
                s += string.charAt(this._cursor++);
            } while(string[this._cursor] !== '"' && !this.isEOF());
            s += '"';
            return {
                "type": "STRING",
                "value": s
            }
        }

    }
}

module.exports = { Tokenizer }