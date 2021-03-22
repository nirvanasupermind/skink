class ArrayList {
    constructor(value) {
        this.value = [...value];
    }
    
    _negIndex(idx) {
        idx = Number.parseFloat(idx);
        if(idx < 0) {
            return this.value.length+idx;
        } else {
            return idx;
        }   
    }


    add(...els) {
        return this.value.push(...els);
    }

    remove(index) {
        index = this._negIndex(index);
        return this.value.splice(index,1);
    }

    get(index) {
        index = this._negIndex(index);
        return this.value[index];
    }


    put(index,val) {
        index = this._negIndex(index);
        return (this.value[index] = val);
    }


}

module.exports = ArrayList;