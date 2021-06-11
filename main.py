from datetime import datetime
import os
from numpy import array
import cv2
import sys
import tempfile
import sounddevice as sd
from scipy.io.wavfile import write


def print_help():
    print("""
    Usage: ./Recorder [OPTION]...
    Record screen and video.

    Options...

        --no-video         record without video
        --no-screen        record without screen capture
        --no-mic           record without user sound
        --no-audio         record without system audio
        --help             to know about this tool
    
    Example...
        
        Ex1: ./Recorder --no-video
        Ex2: ./Recorder --no-video --no-audio
    """)


class Recorder:
    def __init__(self):
        self.args = sys.argv[1:]
        self.video, self.screen, self.mic, self.audio = self.get_details()
        self.file_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.temp_dir = tempfile.gettempdir()

    def get_details(self):
        video = True
        screen = True
        mic = True
        audio = True
        if '--help' in self.args:
            print_help()
            sys.exit()
        if '--no-video' in self.args:
            video = False
        if '--no-screen' in self.args:
            screen = False
        if '--no-mic' in self.args:
            mic = False
        if '--no--audio' in self.args:
            audio = False
        return video, screen, mic, audio


Recorder()
freq = 44100
duration = 5
recording = sd.rec(int(duration * freq), samplerate=freq, channels=2)
sd.wait()
write("recording.wav", freq, recording)
