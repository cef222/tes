import base64

def rc4_ksa(key: str) -> list:
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + ord(key[i % len(key)])) % 256
        S[i], S[j] = S[j], S[i]
    return S

def rc4_prga(S: list, plaintext: str) -> str:
    i = j = 0
    result = ""
    
    for c in plaintext:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        keystream_byte = S[(S[i] + S[j]) % 256]
        result += chr(ord(c) ^ keystream_byte)
    
    return result

def rc4_encrypt(plain: str, key: str) -> str:
    S = rc4_ksa(key)
    encrypted = rc4_prga(S, plain)
    return base64.b64encode(encrypted.encode()).decode()

def rc4_decrypt(cipher: str, key: str) -> str:
    S = rc4_ksa(key)
    decoded = base64.b64decode(cipher).decode()
    return rc4_prga(S, decoded)

def rail_fence_encrypt(text, key: int) -> str:
    # create the matrix to cipher
    # plain text key = rows ,
    # length(text) = columns
    # filling the rail matrix
    # to distinguish filled
    # spaces from blank ones
    try:
        key = int(key)
    except ValueError:
            return "Error: Key harus berupa angka"
    rail = [['\n' for i in range(len(text))]
                for j in range(key)]
     
    # to find the direction
    dir_down = False
    row, col = 0, 0
     
    for i in range(len(text)):
         
        # check the direction of flow
        # reverse the direction if we've just
        # filled the top or bottom rail
        if (row == 0) or (row == key - 1):
            dir_down = not dir_down
         
        # fill the corresponding alphabet
        rail[row][col] = text[i]
        col += 1
         
        # find the next row using
        # direction flag
        if dir_down:
            row += 1
        else:
            row -= 1
    # now we can construct the cipher
    # using the rail matrix
    result = []
    for i in range(key):
        for j in range(len(text)):
            if rail[i][j] != '\n':
                result.append(rail[i][j])
    return("" . join(result))


def rail_fence_decrypt(cipher, key: int) -> str:
    # create the matrix to cipher
    # plain text key = rows ,
    # length(text) = columns
    # filling the rail matrix to
    # distinguish filled spaces
    # from blank ones
    try:
        key = int(key)
    except ValueError:
            return "Error: Key harus berupa angka"
    rail = [['\n' for i in range(len(cipher))]
                for j in range(key)]
     
    # to find the direction
    dir_down = None
    row, col = 0, 0
     
    # mark the places with '*'
    for i in range(len(cipher)):
        if row == 0:
            dir_down = True
        if row == key - 1:
            dir_down = False
         
        # place the marker
        rail[row][col] = '*'
        col += 1
         
        # find the next row
        # using direction flag
        if dir_down:
            row += 1
        else:
            row -= 1
             
    # now we can construct the
    # fill the rail matrix
    index = 0
    for i in range(key):
        for j in range(len(cipher)):
            if ((rail[i][j] == '*') and
            (index < len(cipher))):
                rail[i][j] = cipher[index]
                index += 1
         
    # now read the matrix in
    # zig-zag manner to construct
    # the resultant text
    result = []
    row, col = 0, 0
    for i in range(len(cipher)):
         
        # check the direction of flow
        if row == 0:
            dir_down = True
        if row == key-1:
            dir_down = False
             
        # place the marker
        if (rail[row][col] != '*'):
            result.append(rail[row][col])
            col += 1
             
        # find the next row using
        # direction flag
        if dir_down:
            row += 1
        else:
            row -= 1
    return("".join(result))


def super_encrypt(plaintext: str, keyRail: int, keyRC4: int) -> str:
    step1 = rail_fence_encrypt(plaintext, keyRail)
    return rc4_encrypt(step1, keyRC4)

def super_decrypt(ciphertext: str, keyRail: int, keyRC4: int) -> str:
    step1 = rc4_decrypt(ciphertext, keyRC4)
    return rail_fence_decrypt(step1, keyRail)