ManTable = [ 16, 16, 16, 16,
             16, 0 , 1 , 16,
             16, 2 , 3 , 16,
             16, 16, 16, 16]

def manchester(data):
    decode = ''
    for i in data.split(' '):
        b = int(i,16)
        n = (ManTable[b>>4]<<2)+ManTable[b & 15]
        decode += hex(n)[2] if n<16 else '*'
    if len(decode) == 14:
        ck = 0
        for i in range(0,14,2):
            b = int(decode[i:i+2],16) 
            ck ^= b
    else:
        ck = 10
    print(decode, "-", ck)
