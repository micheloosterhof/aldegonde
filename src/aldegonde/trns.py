"""
Various transposition ciphers
"""


def rail_encrypt(plaintext: str, key: int) -> str:
    """
    function to encrypt a message with railfence

    # create the matrix to cipher
    # plain text key = rows ,
    # length(text) = columns
    # filling the rail matrix to distinguish filled spaces from blank ones
    """
    rail: list[list[str]] = [["\n" for _i in plaintext] for _j in range(key)]

    dir_down: bool = False
    row: int = 0
    col: int

    for col, letter in enumerate(plaintext):
        if (row == 0) or (row == key - 1):
            dir_down = not dir_down
        rail[row][col] = letter
        if dir_down:
            row += 1
        else:
            row -= 1

    result: list[str] = []
    for line in rail:
        for letter in line:
            if letter != "\n":
                result.append(letter)
    return "".join(result)


def rail_decrypt(ciphertext: str, key: int) -> str:
    """
    This function receives cipher-text and key and returns the original
    text after decryption
    """
    rail: list[list[str]] = [["\n" for _i in ciphertext] for _j in range(key)]

    # create the rail matrix and fill with *'s
    dir_down: bool = False
    row: int = 0
    col: int
    for col in range(len(ciphertext)):
        if (row == 0) or (row == key - 1):
            dir_down = not dir_down
        rail[row][col] = "*"
        if dir_down:
            row += 1
        else:
            row -= 1

    # now we can fill the rail matrix with ciphertext values
    index = 0
    for i in range(key):
        for j in range(len(ciphertext)):
            if (rail[i][j] == "*") and (index < len(ciphertext)):
                rail[i][j] = ciphertext[index]
                index += 1

    # now read the matrix in zig-zag manner to construct the resultant text
    result = []
    dir_down = False
    row = 0
    for col in range(len(ciphertext)):
        if (row == 0) or (row == key - 1):
            dir_down = not dir_down
        result.append(rail[row][col])
        if dir_down:
            row += 1
        else:
            row -= 1

    return "".join(result)


def scytale_encrypt(ciphertext: str, key: int) -> str:
    """
    This function receives cipher-text and key and returns the original
    text after decryption
    """
    scytale: list[list[str]] = [["\n" for _i in ciphertext] for _j in range(key)]

    # create the scytale matrix and fill with *'s
    for col in range(len(ciphertext)):
        scytale[col % key][col] = "*"

    # now we can fill the scytale matrix with ciphertext values
    index = 0
    for i in range(key):
        for j in range(len(ciphertext)):
            if (scytale[i][j] == "*") and (index < len(ciphertext)):
                scytale[i][j] = ciphertext[index]
                index += 1

    result = []
    for col in range(len(ciphertext)):
        result.append(scytale[col % key][col])

    return "".join(result)


def scytale_decrypt(plaintext: str, key: int) -> str:
    """
    function to encrypt a message

    # create the matrix to cipher
    # plain text key = rows ,
    # length(text) = columns
    # filling the scytale matrix to distinguish filled spaces from blank ones
    """
    scytale: list[list[str]] = [["" for _i in plaintext] for _j in range(key)]

    for col, letter in enumerate(plaintext):
        scytale[col % key][col] = letter

    print(scytale)

    result: list[str] = []
    for line in scytale:
        for letter in line:
            if letter is not None:
                result.append(letter)
    return "".join(result)


def columnar_transposition_encrypt(message: str, key: str, padding: str = " ") -> str:
    """
    columnar transposition
    """
    message = message.replace(" ", "").upper()
    num_cols = len(key)
    num_rows = -(-len(message) // num_cols)  # Ceiling division
    message += padding * (num_rows * num_cols - len(message))

    # Create an empty matrix to store the message
    matrix: list[list[str]] = [["" for _ in range(num_cols)] for _ in range(num_rows)]

    # Fill the matrix column by column
    index = 0
    for row in range(num_cols):
        for col in range(num_rows):
            matrix[row][col] = message[index]
            index += 1

    # Read the matrix column by column to get the encrypted message
    ciphertext = ""
    for col in range(1, num_cols + 1):
        col_index = key.index(str(col))
        print(col_index)
        for row in range(num_rows):
            ciphertext += matrix[row][col_index]

    return ciphertext


def columnar_transposition_decrypt(ciphertext: str, key: str) -> str:
    """
    columnar transposition
    """
    num_cols = len(key)
    num_rows = len(ciphertext) // num_cols

    # Create an empty matrix to store the encrypted message
    matrix = [["" for _ in range(num_cols)] for _ in range(num_rows)]

    # Calculate the number of characters in the last row
    last_row_chars = len(ciphertext) % num_cols

    # Track the number of characters taken from the encrypted message
    taken_chars = 0

    # Fill the matrix column by column
    for col in range(num_cols):
        col_index = key.index(str(col + 1))
        extra_char = 1 if col_index < last_row_chars else 0

        for row in range(num_rows - extra_char):
            matrix[row][col_index] = ciphertext[taken_chars]
            taken_chars += 1

    # Read the matrix row by row to get the decrypted message
    plaintext = ""
    for row in range(num_rows):
        for col in range(num_cols):
            plaintext += matrix[row][col]

    return plaintext
