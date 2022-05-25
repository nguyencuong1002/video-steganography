#!/usr/bin/env python3
import cv2
import numpy as np
import os
import moviepy.editor
from os import path

def video_to_frames(input_video):
    # change to video folder
    os.chdir("video/")

    #get file path for video
    # input_video = input("Enter Video Name To Encryption: ")
    cap = cv2.VideoCapture(input_video) # default fps: 30
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("fps = " + str(fps))

    # change bak to parent directory
    os.chdir("..")
    path_to_save = './frames'

    current_frame = 0

    while(True):

        #capture each frame
        ret, frame = cap.read()

        #stop loop when video ends
        if not ret:
            break

        # Save frame as a png file
        name = 'frame' + str(current_frame) + '.png'
        
        print ('Creating: ' + name)
        cv2.imwrite(path.join(path_to_save, name), frame)

        #keep track of how many images you end up with
        current_frame += 1

    #release capture 
    cap.release()
    cv2.destroyAllWindows()
    print('Frames saved!')

    # Extract audio from video
    video = moviepy.editor.VideoFileClip(input_video)
    audio = video.audio

    audio.write_audiofile('./video/output.mp3')