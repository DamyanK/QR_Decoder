# QR_Decoder

# About the project
This is the first working version of a QR Code Decoder for steganography. It is entirelly objected to unmask a code,
 stored in a graphical file (.png, .jpg, etc.), read its original message and data stored in 'Error bits'.

# Version 1 QR codes

It is required for the .png image not to contain border around the QR code. If possible to be removed, otherwise the script should be tampered manually. There are test images in the [Tests](Tests) folder and examples on how should masks look when applied in the [Mask Patterns](Mask Patterns) folder.
Recommended size (current version 1): 210x210

# Usage

## Linux

### Decoder
```bash
python3 decoder.py <filename>
```

### get_size.sh
This is a script that returns the size of an image on the X axis.
```bash
chmod +x get_size.sh
./get_size.sh <filename>
```

### resize_img.sh
This script will resize an image, making it a X by X pixel matrix.
```bash
chmod +x resize_img.sh
./resize_img.sh <filename> <size>
```
