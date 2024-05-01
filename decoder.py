from PIL import Image

def load_qr_to_bit_matrix(image_path):
    # Load the QR code image
    qr_code_img = Image.open(image_path)

    # Convert the image to grayscale (if necessary)
    qr_code_img = qr_code_img.convert('L')

    # Convert the image to a bit matrix
    bit_matrix = []
    width, height = qr_code_img.size
    for y in range(height):
        row = []
        for x in range(width):
            # Pixel values in Pillow are in the range 0-255
            # Thresholding at 128 to convert grayscale to binary
            pixel = 1 if qr_code_img.getpixel((x, y)) < 128 else 0
            row.append(pixel)
        bit_matrix.append(row)

    return bit_matrix

# Print formated matrix
def Print(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            print(matrix[i][j], end=" ")
        print()


def ScaleMatrix(scale_from):
    # Test: scaled matrix - Success (?4?/5)
    # 38 is the bit length of the smaller matrix for each bit (cluster size)
    scaled = []

    # fully excluding the border
    for x in range(38, len(scale_from) - 38, 38):
        row = []
        for y in range(38, len(scale_from[0]) - 38, 38):

            # For every bit of a cluster in original matrix, append same bit to
            # a single block cluster in scaled
            if scale_from[x][y] == 0:
                row.append(0)
            else:
                row.append(1)
        scaled.append(row)

    return scaled

def Up(x1, x2, y1, y2, matrix):
    error_bit = ""

    # There are restrictions for the protected bits
    for i in range(x1, x2, -1):
        if i == round(len(scaled) / 3) - 1:
            continue
        for j in range(y1, y2, -1):
            if j == round(len(scaled) / 3) - 1:
                continue
            error_bit += str(matrix[i][j])
    
    return error_bit
        
def Down(x1, x2, y1, y2, matrix):
    error_bit = ""

    # There are restrictions for the protected bits
    for i in range(x1, x2, 1):
        if i == round(len(scaled) / 3) - 1:
            continue
        for j in range(y1, y2, -1):
            if j == round(len(scaled) / 3) - 1:
                continue
            error_bit += str(matrix[i][j])

    return error_bit


# Image to bit matrix (0, 1)
image_path = 'qr-code_chall1_imprime.png'
bit_matrix = load_qr_to_bit_matrix(image_path)


scaled = ScaleMatrix(bit_matrix)


# Unmasking bits (XOR with 1)
# This is for mask 010
# QR is split into 3 equal segments vertically

# 1/3
for i in range(round(len(scaled) / 3) + 2, 2 * round((len(scaled) / 3))):
    if i == round(len(scaled) / 3) or i == 2 * round(len(scaled) / 3) - 1:
        continue
    for j in range(0, round(len(scaled) / 3) - 1, 3):
        scaled[i][j] = scaled[i][j] ^ 1

# 2/3       
for i in range(0, len(scaled)):
    for j in range(round(len(scaled) / 3) + 2, 2 * round((len(scaled) / 3)) - 1, 3):
        if i == round(len(scaled) / 3) - 1 and j % 2 == 0:
            continue
        scaled[i][j] = scaled[i][j] ^ 1

# 3/3
for i in range(round(len(scaled) / 3) + 2, len(scaled)):
    for j in range(2 * round((len(scaled) / 3)) + 1, len(scaled), 3):
        scaled[i][j] = scaled[i][j] ^ 1


# TEST: appending all bits in a string, later splitting into octets
err = ""

# Fix coordinates according to specified segments
# The goal is to divide once again into 3 sectors, one medium on the right,
# large in the middle, and small one on the left
# !! take into account protected bits around the corners !!
X1 = len(scaled) - 1
X2 = round(len(scaled) / 3) + 1
Y1 = len(scaled) - 1
Y2 = Y1 - 2

# Information from segment 3/3
# i is counter for the back 4 double columns of bits
# j is iterator for the columns
for i in range(4): # range is (1/3 size + 1) / 2
    j = i * 2
    if i % 2 == 0:
        err += Up(X1, X2, Y1 - j, Y2 - j, scaled)
    else:
        err += Down(X2 + 1, X1 + 1, Y1 - j, Y2 - j, scaled)

# Segment 2/3
X2 = -1
Y1 = 2 * round(len(scaled) / 3) - 2
Y2 = Y1 - 2

# range for loop is (1/3 size + 1) / 4
err += Up(X1, X2, Y1, Y2, scaled)
err += Down(X2 + 1, X1 + 1, Y1 - 2, Y2 - 2, scaled)

# Segment 1/3

X1 = 2 * round(len(scaled) / 3) - 2
X2 = round(len(scaled) / 3) + 1
Y1 = round(len(scaled) / 3) + 1
Y2 = Y1 - 2

err += Up(X1, X2, Y1, Y2, scaled)
Y1 -= 3
Y2 = Y1 - 2

for i in range(3):
    j = i * 2
    if i % 2 == 0:
        err += Down(X2 + 1, X1 + 1, Y1 - j, Y2 - j, scaled)
    else:
        err += Up(X1, X2, Y1 - j, Y2 - j, scaled)

# Raw bits data
#print(err) 

# Take encryption and length, later based on length will remove Message bits and
# End bits, then split remaining error bits into octets and transform to ASCII
encryption = err[:4]
length = err[:12]
length = length[4:]

message_bits = err[12:]
message_bits = [message_bits[i:i+8] for i in range(0, 8 * int(length, 2), 8)]
message = [chr(int(bit, 2)) for bit in message_bits]
message = ''.join(message)

error_bits = err[int(length, 2) * 8 + 16:]
error_bits = [error_bits[i:i+8] for i in range(0, len(error_bits), 8)]
error_octets = [chr(int(bit, 2)) for bit in error_bits]
error_octets = ''.join(error_octets)

print("### UNMASKED ###\n")
Print(scaled)
print(f"Original message: {message}")
print(f"Hidden data in error bits: {error_octets}")