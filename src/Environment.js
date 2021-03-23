var lynx = require("lynx-js");
var assert = require("assert");
var Int = lynx.Int._.int(32);
var Long = lynx.Int;
var Exception = require("./Exception.js");

/**
 * Environment: names storage.
 */
class Environment {
    /**
     * Creates an Environment with the given record.
     */
    constructor(record = {}, parent = null) {
        this.record = record;
        this.parent = parent;
        // this.define("this",this);
    }

    static clone(original) {
        if (typeof original !== "object" || original == null) { return original; }
        // Use this approach
        //Method 1 - clone will inherit the prototype methods of the original.
        let cloneWithPrototype = Object.assign(Object.create(Object.getPrototypeOf(original)), original);
        return cloneWithPrototype;
    }

    /**
     * Creates a variable with the given name and value.
     */

    define(name, value) {
        // if (this.has(name)) {
        //     throw new Exception(`Identifier '${name}' has already been declared`)
        // }

        this.record[name] = value;
        return value;
    }

    lookup(name) {
        var orig = this.resolve(name).record[name];
        return orig;
    }

    /**
     * Updates an existing variable
     * @param {*} name 
     * @param {*} value 
     */
    assign(name, value) {
        this.resolve(name).record[name] = value;
        return value;
    }

    /**
     * Returns specific Environment in which a variable is defined
     * @param {string} name 
     */
    resolve(name) {
        if (this.record.hasOwnProperty(name)) {
            return this;
        }

        if (this.parent == null) {
            throw new Exception(`Variable ${JSON.stringify(name)} is not defined.`);
        }

        return this.parent.resolve(name);
    }

    has(name) {
        if (this.record.hasOwnProperty(name)) {
            return this;
        }

        if (this.parent == null) {
            return null;
        }

        return this.parent.has(name);
    }
}



module.exports = Environment;