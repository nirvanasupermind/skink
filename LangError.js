class LangError { 
    constructor(msg, offset) {
       this.msg = msg;
       this.offset = offset;
    }
 
    raise() {
       console.log("error: "+ this.msg);
       process.exit();
    }
}

module.exports = LangError;