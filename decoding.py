#!/usr/bin/env python3
import os
import cv2
import sys
import math
import numpy as np
import itertools
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path
from tkinter import *
import tkinter
from tkinter import messagebox
import tkinter.filedialog as fd

from video_to_frames import video_to_frames

b = Tk()
b.title('Video Steganography - Decoding')
b.geometry("500x600")
b['background'] = '#e2f7b5'

quant = np.array([[16, 11, 10, 16, 24, 40, 51, 61],      # QUANTIZATION TABLE
                  [12, 12, 14, 19, 26, 58, 60, 55],    # required for DCT
                  [14, 13, 16, 24, 40, 57, 69, 56],
                  [14, 17, 22, 29, 51, 87, 80, 62],
                  [18, 22, 37, 56, 68, 109, 103, 77],
                  [24, 35, 55, 64, 81, 104, 113, 92],
                  [49, 64, 78, 87, 103, 121, 120, 101],
                  [72, 92, 95, 98, 112, 100, 103, 99]])


class DCT():
    def decode_image(self, img):
        row, col = img.shape[:2]  # include row, col, channels
        messSize = None
        messageBits = []
        buff = 0  # decimal of quantizedBlock

        # split image into RGB channels
        bImg, gImg, rImg = cv2.split(img)

        # break into 8x8 blocks
        imgBlocks = [bImg[j:j+8, i:i+8]-128 for (j, i) in itertools.product(range(0, row, 8),  # get each block 8x8 in image
                                                                            range(0, col, 8))]

        # blocks run through quantization table
        # quantization
        quantizedDCT = [img_Block/quant for img_Block in imgBlocks]

        i = 0
        # message extracted from LSB of DC coeff
        for quantizedBlock in quantizedDCT:
            DC = quantizedBlock[0][6]
            DC = np.uint8(DC)
            DC = np.unpackbits(DC)
            # print(DC)
            if DC[7] == 1:
                # shift left (7-i) bits | cause 1 char in hid mess has 8bit
                buff += (0 & 1) << (7-i)
            elif DC[7] == 0:
                buff += (1 & 1) << (7-i)

            i = 1+i
            if i == 8:
                messageBits.append(chr(buff))

                buff = 0
                i = 0
                if messageBits[-1] == '*' and messSize is None:
                    try:
                        messSize = int(''.join(messageBits[:-1]))
                        print('-->Length Message: ' + str(messSize))
                        mess_size = Label(
                            b, font=('Arial', 10), text="Secret Message is: " + str(messSize), fg='red')
                        mess_size.place(x=40, y=140)
                    except:
                        pass
            if len(messageBits) - len(str(messSize)) - 1 == messSize:
                # return mess from index(*)+1 ->end
                return ''.join(messageBits)[len(str(messSize))+1:]

        return ''


# tạo ra label output_video
lb_output_video = Label(b, font=('Arial', 10), text='Input video')
lb_output_video.place(x=10, y=10)

# Tạo ra entry output video
output_video = Entry(b, width=30, font=('Times New Roman', 10))
output_video.pack()
output_video.place(x=120, y=10)
output_video.focus()

# Upload file
def upload_file():
    file = fd.askopenfilename(initialdir=os.getcwd(), title='Chọn tập tin')
    if(file):
        output_video.delete(0, END)
        output_video.insert(0, file)

btn_upload_file_o = Button(b, text="Select File", width=10, height=1, font=(
    'Times New Roman', 10), command=upload_file)
btn_upload_file_o.place(x=320, y=10)

# Run main
def main_decode():

    # get frames from encoded video
    # input("Enter Video Name To Decode: ")
    print("Process-Decode is running ......")
    path = "./frames/"
    files = [f for f in os.listdir(path) if not f.startswith('.')]
    for file in files:
        filename = os.path.join(path, file)
        img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
        hidden_text = DCT().decode_image(img)
        if hidden_text != "":
            # print(f'-->Message Received: {hidden_text}')
            mess_information = Label(
                b, font=('Arial', 10), text="Secret Message is: " + str(hidden_text), fg='red')
            mess_information.place(x=40, y=160)
            break

btn_decode = Button(b, text="Decoding", width=10, height=1,
                    font=('Times New Roman', 10), command=main_decode)
btn_decode.place(x=80, y=100)
# if __name__ == "__main__":
#     main()

# b.mainloop()
