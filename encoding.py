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
# import moviepy.editor


from video_to_frames import video_to_frames
from frames_to_video import frames_to_video

a = Tk()
a.title('Video Steganography - Encoding')
a.geometry("500x600")
a['background'] = '#e2f7b5'
# a.eval('tk::PlaceWindow . center')

quant = np.array([[16, 11, 10, 16, 24, 40, 51, 61],      # QUANTIZATION TABLE
                  [12, 12, 14, 19, 26, 58, 60, 55],    # required for DCT
                  [14, 13, 16, 24, 40, 57, 69, 56],
                  [14, 17, 22, 29, 51, 87, 80, 62],
                  [18, 22, 37, 56, 68, 109, 103, 77],
                  [24, 35, 55, 64, 81, 104, 113, 92],
                  [49, 64, 78, 87, 103, 121, 120, 101],
                  [72, 92, 95, 98, 112, 100, 103, 99]])


class DCT():
    def __init__(self):  # Constructor
        self.message = None
        self.bitMess = None
        self.oriCol = 0
        self.oriRow = 0

    # encoding part :
    def encode_image(self, img, secret_msg):
        # show(img)
        secret = secret_msg
        self.message = str(len(secret))+'*'+secret
        self.bitMess = self.toBits()

        # get size of image in pixels
        row, col = img.shape[:2]
        ##col, row = img.size

        self.oriRow, self.oriCol = row, col
        if((col/8)*(row/8) < len(secret)):
            print("Error: Message too large to encode in image")
            return False

        # make divisible by 8x8
        if row % 8 != 0 or col % 8 != 0:
            img = self.addPadd(img, row, col)

        row, col = img.shape[:2]
        ##col, row = img.size

        # split image into RGB channels
        bImg, gImg, rImg = cv2.split(img)

        # message to be hid in blue channel so converted to type float32 for dct function
        bImg = np.float32(bImg)

        # break into 8x8 blocks
        imgBlocks = [np.round(bImg[j:j+8, i:i+8]-128) for (j, i) in itertools.product(range(0, row, 8),
                                                                                      range(0, col, 8))]

        # Blocks are run through DCT function
        dctBlocks = [np.round(cv2.dct(img_Block)) for img_Block in imgBlocks]

        # blocks then run through quantization table
        quantizedDCT = [np.round(dct_Block/quant) for dct_Block in dctBlocks]

        # set LSB in DC value corresponding bit of message
        messIndex = 0
        letterIndex = 0
        for quantizedBlock in quantizedDCT:

            # find LSB in DC coeff and replace with message bit
            DC = quantizedBlock[0][6]
            DC = np.uint8(DC)
            DC = np.unpackbits(DC)
            DC[7] = self.bitMess[messIndex][letterIndex]
            DC = np.packbits(DC)
            DC = np.float32(DC)
            DC = DC-255
            quantizedBlock[0][6] = DC
            letterIndex = letterIndex+1
            if letterIndex == 8:
                letterIndex = 0
                messIndex = messIndex + 1
                if messIndex == len(self.message):
                    break

        # blocks run inversely through quantization table
        sImgBlocks = [quantizedBlock * quant +
                      128 for quantizedBlock in quantizedDCT]
        # blocks run through inverse DCT
        #sImgBlocks = [cv2.idct(B)+128 for B in quantizedDCT]

        # puts the new image back together
        sImg = []
        for chunkRowBlocks in self.chunks(sImgBlocks, col/8):
            for rowBlockNum in range(8):
                for block in chunkRowBlocks:
                    sImg.extend(block[rowBlockNum])
        sImg = np.array(sImg).reshape(row, col)

        # converted from type float32
        sImg = np.uint8(sImg)
        # show(sImg)
        sImg = cv2.merge((sImg, gImg, rImg))
        return sImg

    def chunks(self, l, n):
        m = int(n)
        for i in range(0, len(l), m):
            yield l[i:i + m]

    def toBits(self):
        bits = []
        for char in self.message:
            binval = bin(ord(char))[2:].rjust(8, '0')
            bits.append(binval)
        return bits


# tạo ra label Input_video
lb_input_video = Label(a, font=('Arial', 10), text='Input video')
lb_input_video.place(x=10, y=10)
# Tạo label Message
lb_secret_msg = Label(a, font=('Arial', 10), text='Secret Message')
lb_secret_msg.place(x=10, y=50)

# Tạo ra entry input video
input_video = Entry(a, width=30, font=('Times New Roman', 10))
input_video.pack()
input_video.place(x=120, y=10)
input_video.focus()
# Tạo ra entry secret message
secret_msg = Entry(a, width=30, font=('Times New Roman', 10))
secret_msg.place(x=120, y=50)

# Upload file video
def upload_file():
    file = fd.askopenfilename(initialdir=os.getcwd(), title='Chọn tập tin')
    if(file):
        input_video.delete(0, END)
        input_video.insert(0, file)

btn_upload_file = Button(a, text="Select File", width=10, height=1, font=(
    'Times New Roman', 10), command=upload_file)
btn_upload_file.place(x=320, y=10)


def main_encode():
    # ms_process = Label(a, font=('Arial', 10), text = "Encoding is processing....", fg='red')
    # ms_process.place(x = 40, y = 120)

    # get frames from video
    video_to_frames(input_video.get())
    # change dir
    os.chdir("frames/")

    # choose frame to encode
    img_name = "frame10.png"
    if not os.path.isfile(img_name):
        raise Exception("Image not found")
    print("Chose frame10.png to encode")

    img = cv2.imread(img_name, cv2.IMREAD_UNCHANGED)
    # Mã hoá secret mess vào image
    encoded_img = DCT().encode_image(img, secret_msg.get())
    cv2.imwrite(img_name, encoded_img)
    os.chdir("..")

    # build encoded video
    frames_to_video()

    # secret_msg = input("-->Enter Secret Message To Hide: ")
    # print("Message length is: " + str(len(secret_msg.get())))
    # Show message info & length
    mess_info = Label(a, font=(
        'Arial', 10), text="Secret Message is: " + str(secret_msg.get()), fg='red')
    mess_info.place(x=40, y=140)

    mess_length = Label(a, font=(
        'Arial', 10), text="Secret Message Length is: " + str(len(secret_msg.get())), fg='red')
    mess_length.place(x=40, y=160)

    ms_output = Label(a, font=('Arial', 10),
                      text="final.mp4 is saved in Folder video", fg='red')
    ms_output.place(x=40, y=180)
    messagebox.showinfo("Encoding", "Encoding Successfully!!!")

btn_encode = Button(a, text="Encoding", width=10, height=1,
                    font=('Times New Roman', 10), command=main_encode)
btn_encode.place(x=80, y=100)
# if __name__ == "__main__":
#     main()
a.mainloop()
