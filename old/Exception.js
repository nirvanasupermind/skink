class Exception extends Error {
    constructor(message) {
        this.message = message;
        this.name = "Exception"
    }
} 

module.exports = Exception;