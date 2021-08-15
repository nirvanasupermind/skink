from values import *
class Interpreter:
    def __init__(self):
        pass

    def eval(self, exp):
        if exp == None:
            return Null()
        if exp[0] == 'int':
            return self.eval_int(exp)
        elif exp[0] == 'float':
            return self.eval_float(exp)
        elif exp[0] == 'plus':
            return self.eval_plus(exp)
        elif exp[0] == 'minus':
            return self.eval_minus(exp)
        elif exp[0] == 'mul':
            return self.eval_mul(exp)
        elif exp[0] == 'div':
            return self.eval_div(exp)
        else:
            raise Exception('Unimplemented')

    def eval_int(self, exp):
        token = exp[1]
        tmp = np.clip(int(token.value), -2**63, 2**63-1) 
        return Int(np.int64(tmp))
    
    def eval_float(self, exp):
        token = exp[1]
        return Float(float(token.value))
    
    def eval_plus(self, exp):
        left = self.eval(exp[1])
        right = self.eval(exp[2])

        return left + right

    def eval_minus(self, exp):
        left = self.eval(exp[1])
        right = self.eval(exp[2])
        
        return left - right
    
    def eval_mul(self, exp):
        left = self.eval(exp[1])
        right = self.eval(exp[2])
        
        return left * right

    def eval_div(self, exp):
        left = self.eval(exp[1])
        right = self.eval(exp[2])
        
        return left / right