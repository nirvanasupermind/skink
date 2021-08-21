import numpy as np
import struct

# https://stackoverflow.com/questions/16444726/binary-representation-of-float-in-python-bits-not-hex
def binary(num):
    return ''.join('{:0>8b}'.format(c) for c in struct.pack('!f', num))

def highbits(x):
    return x & 0xffffffff
    
def lowbits(x):
    return ((x >> 32) << 32)

def hash_float(x):
    return hash(np.int64(int(binary(x), 2)))

# https://stackoverflow.com/questions/5832982/how-to-get-the-logical-right-binary-shift-in-python
def rshift(val, n): return val>>n if val >= 0 else (val+0x100000000)>>n