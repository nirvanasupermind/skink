class Exception extends Error {
    constructor(message) {
        super(message);
        this.name = "Exception";
        this.message = message;
    }
}

module.exports = Exception;