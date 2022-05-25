#!/usr/bin/env python3
import cv2
import numpy as np
from os import listdir
from os.path import join, isfile
import moviepy.editor
from decoding import DCT

def frames_to_video():
    path = "./frames"

    frames = []

    # ignore .DS_Store
    files = [f for f in listdir(path) if not f.startswith('.')]

    # sort files in correct order
    files.sort(key=lambda x: int(x[5:-4])) # x[5:-4] is the number
    # print(files)

    for f in files:
        filename = join(path, f)

        # reading each file
        img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
        height, width, channels = img.shape
        size = (width, height)

        # append img to frames array
        frames.append(img)

    fps = 30
    output = cv2.VideoWriter('./video/output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

    # # test
    # for img in frames:
    #     hidden_text = DCT().decode_image(img)
    #     if hidden_text != "":
    #         print(hidden_text)
    #         break

    # writting image to video
    for img in frames:
        output.write(img)

    output.release()
    # print("---Encoded Successfully - saved in Folder Video!---")

    # Combine audio into video
    input_video = "./video/output.mp4"
    input_audio = "./video/output.mp3"
    output_video = "./video/final.mp4"

    videoClip = moviepy.editor.VideoFileClip(input_video)
    audioClip = moviepy.editor.AudioFileClip(input_audio)

    finalClip = videoClip.set_audio(audioClip)
    finalClip.write_videofile(output_video, fps)

