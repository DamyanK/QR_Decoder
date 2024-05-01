#!/usr/bin/env python3

import sys
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

def ScaleMatrix(scale_from):
    # 38 is the bit length of the smaller matrix for each bit (cluster size)
    scaled = []
    # If cluster is a little offset, can always be changed 
    # according to offset
    cluster_size = 38

    # fully excluding the border
    for x in range(cluster_size, len(scale_from) - cluster_size, cluster_size):
        row = []
        for y in range(cluster_size, len(scale_from[0]) - cluster_size, cluster_size):

            # For every bit of a cluster in original matrix, append same bit to
            # a single block cluster in scaled
            if scale_from[x][y] == 0:
                row.append(0)
            else:
                row.append(1)
        scaled.append(row)

    return scaled

def FindMask(matrix):
    # For coordinates, mask bits are two bits away from the
    # bottom of the QR code, and 2 bits on the right of the
    # bottom left position pattern
    x = len(matrix) - 3
    y = round(len(matrix) / 3) + 1

    return [1 ^ matrix[x - i][y] if i % 2 == 0 else 0 ^ matrix[x - i][y] for i in range(3)]

def MaskPattern010(matrix):
    # This is for mask 010
    # QR is split into 3 equal segments vertically

    # 1/3
    for i in range(round(len(matrix) / 3) + 2, 2 * round((len(matrix) / 3)) - 1):
        for j in range(0, round(len(matrix) / 3) - 1, 3):
            matrix[i][j] = matrix[i][j] ^ 1

    # 2/3       
    for i in range(0, len(matrix)):
        for j in range(round(len(matrix) / 3) + 2, 2 * round((len(matrix) / 3)) - 1, 3):
            if i == round(len(matrix) / 3) - 1 and j % 2 == 0:
                continue
            matrix[i][j] = matrix[i][j] ^ 1

    # 3/3
    for i in range(round(len(matrix) / 3) + 2, len(matrix)):
        for j in range(2 * round((len(matrix) / 3)) + 1, len(matrix), 3):
            matrix[i][j] = matrix[i][j] ^ 1

    return matrix


def Up(x1, x2, y1, y2, matrix):
    error_bit = ""

    # There are restrictions for the protected bits
    for i in range(x1, x2, -1):
        if i == round(len(matrix) / 3) - 1:
            continue
        for j in range(y1, y2, -1):
            if j == round(len(matrix) / 3) - 1:
                continue
            error_bit += str(matrix[i][j])
    
    return error_bit
        
def Down(x1, x2, y1, y2, matrix):
    error_bit = ""

    # There are restrictions for the protected bits
    for i in range(x1, x2, 1):
        if i == round(len(matrix) / 3) - 1:
            continue
        for j in range(y1, y2, -1):
            if j == round(len(matrix) / 3) - 1:
                continue
            error_bit += str(matrix[i][j])

    return error_bit

# Print formated matrix
def Print(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            print(matrix[i][j], end=" ")
        print()

def GetDataBits(matrix):
    # Appending all bits in a string, later splitting into octets
    err = ""

    # Fix coordinates according to specified segments
    # The goal is to divide once again into 3 sectors, one medium on the right,
    # large in the middle, and small one on the left
    # !! take into account protected bits around the corners !!
    X1 = len(matrix) - 1
    X2 = round(len(matrix) / 3) + 1
    Y1 = len(matrix) - 1
    Y2 = Y1 - 2

    # Information from segment 3/3
    # i is counter for the back 4 double columns of bits
    # j is iterator for the columns
    for i in range(4): # range is (1/3 size + 1) / 2
        j = i * 2
        if i % 2 == 0:
            err += Up(X1, X2, Y1 - j, Y2 - j, matrix)
        else:
            err += Down(X2 + 1, X1 + 1, Y1 - j, Y2 - j, matrix)

    # Segment 2/3
    X2 = -1
    Y1 = 2 * round(len(matrix) / 3) - 2
    Y2 = Y1 - 2

    # range for loop is (1/3 size + 1) / 4
    err += Up(X1, X2, Y1, Y2, matrix)
    err += Down(X2 + 1, X1 + 1, Y1 - 2, Y2 - 2, matrix)

    # Segment 1/3

    # Octet before protected bits
    X1 = 2 * round(len(matrix) / 3) - 2
    X2 = round(len(matrix) / 3) + 1
    Y1 = round(len(matrix) / 3) + 1
    Y2 = Y1 - 2

    err += Up(X1, X2, Y1, Y2, matrix)
    Y1 -= 3
    Y2 = Y1 - 2

    # Octets after protected bits
    # range for loop is ((1/3 size - 1) / 2)
    for i in range(3):
        j = i * 2
        if i % 2 == 0:
            err += Down(X2 + 1, X1 + 1, Y1 - j, Y2 - j, matrix)
        else:
            err += Up(X1, X2, Y1 - j, Y2 - j, matrix)
    
    return err

def main(arg):
    # Image to bit matrix (0, 1)
    image_path = arg
    bit_matrix = load_qr_to_bit_matrix(image_path)

    # Getting the original scaled matrix and mask pattern
    scaled = ScaleMatrix(bit_matrix)
    mask = [str(bit) for bit in FindMask(scaled)]
    mask = ''.join(mask)

    # Unmasking bits (XOR with 1)

    if mask == "000":
        pass
    elif mask == "001":
        pass
    elif mask == "010":
        scaled = MaskPattern010(scaled)
    elif mask == "011":
        pass
    elif mask == "100":
        pass
    elif mask == "101":
        pass
    elif mask == "110":
        pass
    elif mask == "111":
        pass


    # Operations on unmasked qr code
    raw = GetDataBits(scaled)
    # Raw bits data
    #print(err) 

    # Take encryption and length, later based on length will remove Message bits and
    # End bits, then split remaining error bits into octets and transform to ASCII
    encryption = raw[:4]
    length = raw[:12]
    length = length[4:]

    message_bits = raw[12:]
    message_bits = [message_bits[i:i+8] for i in range(0, 8 * int(length, 2), 8)]
    message = [chr(int(bit, 2)) for bit in message_bits]
    message = ''.join(message)

    error_bits = raw[int(length, 2) * 8 + 16:]
    error_bits = [error_bits[i:i+8] for i in range(0, len(error_bits), 8)]
    error_octets = [chr(int(bit, 2)) for bit in error_bits]
    error_octets = ''.join(error_octets)

    #print("### UNMASKED ###\n")
    #Print(scaled)
    print(f"Original message: {message}")
    print(f"Hidden data in error bits: {error_octets}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: decoder.py <path-to-file>\nEx: decoder.py qrcode.png")
    else:
        arg = sys.argv[1]
        main(arg)
    